package feature.login.impl

import androidx.compose.runtime.Composable
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import feature.common.compose.ObserveAsEvent
import feature.login.impl.components.LoginContent
import feature.login.impl.state.SideEffect
import org.koin.androidx.compose.koinViewModel

@Composable
fun LoginScreen(
    onSuccessLogin: () -> Unit,
    navigateToRegister: () -> Unit,
    navigateToForgotPassword: () -> Unit
) {
    val viewModel: LoginViewModel = koinViewModel()

    LoginContent(
        state = viewModel.state.collectAsStateWithLifecycle().value,
        action = viewModel::processAction
    )

    ObserveAsEvent(viewModel.sideEffect) { sideEffect ->
        when (sideEffect) {
            SideEffect.SuccessLogin -> onSuccessLogin()
            SideEffect.NavigateToRegister -> navigateToRegister()
            SideEffect.NavigateToForgotPassword -> navigateToForgotPassword()
        }
    }
}