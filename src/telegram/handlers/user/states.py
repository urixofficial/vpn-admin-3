from aiogram.fsm.state import StatesGroup, State


class UserRegistrationStates(StatesGroup):
	enter_name = State()
	confirmation = State()
