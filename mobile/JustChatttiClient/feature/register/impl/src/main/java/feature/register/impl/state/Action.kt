package feature.register.impl.state

sealed interface RegisterAction {
    data class ChangeLogin(val value: String): RegisterAction
    data class ChangePassword(val value: String): RegisterAction
    data class ChangePasswordConfirm(val value: String): RegisterAction
    data object OnRegister: RegisterAction
    data object HasAccount: RegisterAction
}