from enum import Enum

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from middleware.only_doctor import only_doctor

from database import Session
from models import User
from routers.auth import get_user
from schemas.appointment_schema import (AppointmentBase, AppointmentCreate,
                                        AppointmentCustomerResponse,
                                        AppointmentsDoctorResponse,
                                        SuccessResponse)
from services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


class ModelType(str, Enum):
    doctor = "doctor"
    clinic = "clinic"
    pharmacy = "pharmacy"


@router.get("/doctor", response_model=list[AppointmentsDoctorResponse])
async def get_appointments_doctors(
    db: Session,
    user_id: int = Depends(get_user)
):
    """İstifadəçinin doktorlarla bağlı randevularını gətir"""
    return await AppointmentService.get_appointments_by_model_type(db, user_id)


@router.get("/customer", response_model=list[AppointmentCustomerResponse])
async def get_appointments_customer(
    db: Session,
    user: User = Depends(only_doctor)
):
    """Doktorun müştəri randevularını gətir"""
    return await AppointmentService.get_customer_appointments(db, user)


@router.post("/{model_type}/{model_id}", response_model=AppointmentBase)
async def create_appointment(
    model_type: ModelType,
    model_id: int,
    item: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int = Depends(get_user),
):
    """Yeni randevu yarat"""
    return await AppointmentService.create_appointment(
        db=db,
        model_type=model_type.value,
        model_id=model_id,
        appointment_data=item,
        user_id=user_id,
        background_tasks=background_tasks
    )


@router.get("/accept/{appointment_id}", response_model=SuccessResponse)
async def accept_appointment(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    db: Session,
    user: User = Depends(only_doctor)
):
    """Randevunu qəbul et"""
    await AppointmentService.accept_appointment(
        db=db,
        appointment_id=appointment_id,
        doctor_user=user,
        background_tasks=background_tasks
    )
    return {"message": "Appointment accepted"}


@router.get("/complete/{appointment_id}", response_model=SuccessResponse)
async def complete_appointment(
    appointment_id: int,
    db: Session,
    user: User = Depends(only_doctor)
):
    """Randevunu tamamla"""
    await AppointmentService.complete_appointment(
        db=db,
        appointment_id=appointment_id,
        doctor_user=user
    )
    return {"message": "Appointment completed"}


@router.put("/{appointment_id}/cancel", response_model=SuccessResponse)
async def cancel_appointment(
    appointment_id: int,
    reason: str = Query(..., min_length=3, description="Ləğv səbəbi"),
    db: Session,
    user_id: int = Depends(get_user)
):
    """Randevunu ləğv et"""
    await AppointmentService.cancel_appointment(
        db=db,
        appointment_id=appointment_id,
        reason=reason,
        user_id=user_id
    )
    return {"message": "Appointment cancelled"}
