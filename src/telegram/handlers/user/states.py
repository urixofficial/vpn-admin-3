from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
	enter_name = State()
	confirmation = State()
