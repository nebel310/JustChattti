package feature.register.impl

import androidx.compose.runtime.Composable
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import core.common.exceptions.NetworkException
import core.common.exceptions.isBadRequest
import core.common.exceptions.isServerError
import feature.common.compose.ObserveAsEvent
import feature.register.impl.components.RegisterContent
import feature.register.impl.state.SideEffect
import org.koin.androidx.compose.koinViewModel

@Composable
fun RegisterScreen(
    navigateToLogin: () -> Unit
) {
    val viewModel: RegisterViewModel = koinViewModel()

    RegisterContent(
        state = viewModel.state.collectAsStateWithLifecycle().value,
        action = viewModel::processAction
    )

    ObserveAsEvent(viewModel.sideEffect) { sideEffect ->
        when (sideEffect) {
            SideEffect.SuccessRegister -> navigateToLogin()
            SideEffect.HasAccount -> navigateToLogin()
        }
    }
}