from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from database import Session, SessionLocal
from models import Appointment, Chat, Customer, Doctor, User
from models.appointment import AppointmentStatus
from schemas.appointment_schema import AppointmentCreate
from services.notification_service import NotificationService


class AppointmentService:
    @staticmethod
    async def get_appointment_by_id(
        db: Session, appointment_id: int, with_customer: bool = False
    ) -> Appointment:
        """Appointment-i ID-yə görə gətir"""
        query = select(Appointment).where(Appointment.id == appointment_id)

        if with_customer:
            query = query.options(
                selectinload(Appointment.customer).selectinload(Customer.user)
            )

        result = await db.exec(query)
        appointment = result.first()

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment tapılmadı")

        return appointment

    @staticmethod
    async def get_appointments_by_model_type(db: Session, user_id: int):
        """İstifadəçinin model tipinə görə randevularını gətir"""
        # Customer-i tap
        customer_query = select(Customer).where(Customer.user_id == user_id)
        customer_result = await db.exec(customer_query)
        customer = customer_result.first()

        if not customer:
            raise HTTPException(status_code=404, detail="Customer tapılmadı")

        # Randevuları gətir
        query = (
            select(
                Appointment.id.label("appointment_id"),
                Appointment.date,
                Doctor.id.label("doctor_id"),
                Doctor.clinic,
                Doctor.category_id,
                User.id.label("user_id"),
                User.name,
                User.image,
            )
            .join(Doctor, Appointment.model_id == Doctor.id)
            .join(User, Doctor.user_id == User.id)
            .where(
                Appointment.customer_id == customer.id,
                Appointment.model_type == "doctor",
            )
        )

        result = await db.exec(query)
        appointments = result.all()

        if not appointments:
            raise HTTPException(status_code=404, detail="Appointment tapılmadı")

        return [
            {
                "id": item.doctor_id,
                "appointment_id": item.appointment_id,
                "clinic": item.clinic,
                "user": {
                    "id": item.user_id,
                    "name": item.name,
                    "image": item.image,
                },
                "doctor_category": {
                    "id": item.category_id,
                    "title": "",  # Category title əlavə edilməlidir
                },
                "has_favorited": False,  # Bu məlumat əlavə edilməlidir
                "average_rating": 0.0,  # Bu məlumat əlavə edilməlidir
                "date": item.date,
            }
            for item in appointments
        ]

    @staticmethod
    async def get_customer_appointments(db: Session, doctor_user: User):
        """Doktorun müştəri randevularını gətir"""
        # Doctor-u tap
        doctor_query = select(Doctor).where(Doctor.user_id == doctor_user.id)
        doctor_result = await db.exec(doctor_query)
        doctor = doctor_result.first()

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor tapılmadı")

        # Randevuları gətir
        query = (
            select(Appointment)
            .options(selectinload(Appointment.customer).selectinload(Customer.user))
            .where(
                Appointment.model_id == doctor.id, Appointment.model_type == "doctor"
            )
        )

        result = await db.exec(query)
        appointments = result.all()

        if not appointments:
            raise HTTPException(status_code=404, detail="Appointment tapılmadı")

        return [
            {
                "id": appointment.id,
                "full_name": appointment.full_name,
                "phone": appointment.phone,
                "image": appointment.customer.user.image,
                "complaint": appointment.complaint,
                "status": appointment.status,
                "fin_code": appointment.fin_code,
                "date": appointment.date,
            }
            for appointment in appointments
        ]

    @staticmethod
    async def create_appointment(
        db: Session,
        model_type: str,
        model_id: int,
        appointment_data: AppointmentCreate,
        user_id: int,
        background_tasks: BackgroundTasks,
    ) -> Appointment:
        """Yeni randevu yarat"""
        # Customer-i tap
        customer_query = select(Customer).where(Customer.user_id == user_id)
        customer_result = await db.exec(customer_query)
        customer = customer_result.first()

        if not customer:
            raise HTTPException(status_code=404, detail="Customer tapılmadı")

        # Yeni appointment yarat
        appointment = Appointment(
            customer_id=customer.id,
            model_type=model_type,
            model_id=model_id,
            full_name=appointment_data.full_name,
            phone=appointment_data.phone,
            complaint=appointment_data.complaint,
            fin_code=appointment_data.fin_code,
            date=appointment_data.date,
            status=AppointmentStatus.PENDING,
        )

        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)

        # Bildiriş göndər
        if model_type == "doctor":
            doctor_query = (
                select(Doctor)
                .options(selectinload(Doctor.user))
                .where(Doctor.id == model_id)
            )
            doctor_result = await db.exec(doctor_query)
            doctor = doctor_result.first()

            if doctor:

                async def notify():
                    async with AsyncSession() as new_db:
                        await NotificationService.create_notification(
                            db=new_db,
                            user_id=doctor.user_id,
                            title="Yeni Rezervasiya",
                            content=f"{appointment_data.full_name} sizinlə görüş təyin etdi.",
                            image=doctor.user.image if doctor.user.image else "",
                            path=f"/accept/{appointment.id}",
                        )

                background_tasks.add_task(notify)

        return appointment

    @staticmethod
    async def accept_appointment(
        db: Session,
        appointment_id: int,
        doctor_user: User,
        background_tasks: BackgroundTasks,
    ):
        """Randevunu qəbul et"""
        appointment = await AppointmentService.get_appointment_by_id(
            db, appointment_id, with_customer=True
        )

        # Statusu dəyiş
        appointment.status = AppointmentStatus.ACCEPTED

        customer_user_id = appointment.customer.user_id
        customer_name = appointment.customer.user.name
        customer_image = appointment.customer.user.image or ""

        # Chat yarat və ya aktiv et
        if appointment.model_type == "doctor":
            doctor_query = select(Doctor).where(Doctor.id == appointment.model_id)
            doctor_result = await db.exec(doctor_query)
            doctor = doctor_result.first()

            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor tapılmadı")

            # Chat-i yoxla
            chat_query = select(Chat).where(
                Chat.user1_id == doctor.user_id, Chat.user2_id == customer_user_id
            )
            chat_result = await db.exec(chat_query)
            chat = chat_result.first()

            if chat:
                chat.is_closed = True
            else:
                chat = Chat(
                    user1_id=doctor.user_id, user2_id=customer_user_id, is_closed=True
                )
                db.add(chat)

            await db.commit()
            await db.refresh(chat)

        await db.commit()
        await db.refresh(appointment)

        # Bildiriş göndər
        if appointment.model_type == "doctor":
            doctor_query = (
                select(Doctor)
                .options(selectinload(Doctor.user))
                .where(Doctor.id == appointment.model_id)
            )
            doctor_result = await db.exec(doctor_query)
            doctor = doctor_result.first()

            if doctor:

                async def notify():
                    async with SessionLocal() as new_db:
                        await NotificationService.create_notification(
                            db=new_db,
                            user_id=doctor.user_id,
                            title="Rezervasiyanız qəbul edildi",
                            content=f"{customer_name} Sizin rezervasiyanızı qəbul etdi.",
                            image=customer_image,
                            path=f"/accept/{appointment.id}",
                        )

                background_tasks.add_task(notify)

    @staticmethod
    async def complete_appointment(db: Session, appointment_id: int, doctor_user: User):
        """Randevunu tamamla"""
        appointment = await AppointmentService.get_appointment_by_id(
            db, appointment_id, with_customer=True
        )

        # Statusu dəyiş
        appointment.status = AppointmentStatus.COMPLETED

        # Chat-i bağla
        chat_query = select(Chat).where(
            Chat.user1_id == appointment.customer.user_id,
            Chat.user2_id == doctor_user.id,
        )
        chat_result = await db.exec(chat_query)
        chat = chat_result.first()

        if chat:
            chat.is_closed = False
            await db.commit()
            await db.refresh(chat)

        await db.commit()
        await db.refresh(appointment)

    @staticmethod
    async def cancel_appointment(
        db: Session, appointment_id: int, reason: str, user_id: int
    ):
        """Randevunu ləğv et"""
        appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)

        # İcazə yoxla
        customer_query = select(Customer).where(Customer.user_id == user_id)
        customer_result = await db.exec(customer_query)
        customer = customer_result.first()

        if not customer or appointment.customer_id != customer.id:
            raise HTTPException(
                status_code=403, detail="Bu randevunu ləğv etmək səlahiyyətiniz yoxdur"
            )

        # Statusu dəyiş
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = reason

        await db.commit()
        await db.refresh(appointment)
