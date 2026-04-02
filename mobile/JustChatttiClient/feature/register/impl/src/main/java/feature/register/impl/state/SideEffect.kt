package feature.register.impl.state

sealed interface SideEffect {
    data object SuccessRegister : SideEffect
    data object HasAccount : SideEffect
}