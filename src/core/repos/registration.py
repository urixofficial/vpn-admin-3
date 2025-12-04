from core.models.registration import RegistrationModel
from core.schemas.registration import CreateRegistration, ReadRegistration, UpdateRegistration

from .base import BaseRepo


class RegistrationRepo(BaseRepo[CreateRegistration, ReadRegistration, UpdateRegistration, RegistrationModel]):
	pass


registration_repo = RegistrationRepo(CreateRegistration, ReadRegistration, UpdateRegistration, RegistrationModel)
