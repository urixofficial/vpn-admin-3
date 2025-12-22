from aiogram.fsm.state import StatesGroup, State


class UserRegistrationStates(StatesGroup):
	enter_name = State()
	enter_description = State()
	confirmation = State()

class UserInstructionsState(StatesGroup):
	choose = State()


class UserPaymentStates(StatesGroup):
	enter_amount = State()
	confirmation = State()
