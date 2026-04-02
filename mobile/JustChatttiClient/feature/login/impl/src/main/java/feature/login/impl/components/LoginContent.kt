package feature.login.impl.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.justchattticlient.uikit.R
import feature.login.impl.state.LoginAction
import feature.login.impl.state.LoginState
import kotlinx.coroutines.flow.collectLatest
import uikit.components.ButtonWithLoader
import uikit.space16
import uikit.space20
import uikit.space24
import uikit.space28
import uikit.space32
import uikit.theme.JustChatttiClientTheme

@Composable
internal fun LoginContent(
    state: LoginState,
    action: (LoginAction) -> Unit
) {
    val textEmailState = rememberTextFieldState(state.login)
    val textPassState = rememberTextFieldState(state.password)
    val isButtonEnabled = remember {
        textEmailState.text.isNotBlank() &&
                textPassState.text.isNotBlank()
    }

    LaunchedEffect(Unit) {
        snapshotFlow { textEmailState.text }
            .collectLatest {
                action(LoginAction.ChangeLogin(it.toString()))
            }
    }

    LaunchedEffect(Unit) {
        snapshotFlow { textPassState.text }
            .collectLatest {
                action(LoginAction.ChangePassword(it.toString()))
            }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(space16)
            .statusBarsPadding(),
        contentAlignment = BiasAlignment(horizontalBias = 0f, verticalBias = -0.3f)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .imePadding()
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(modifier = Modifier.fillMaxWidth(),
                text = stringResource(R.string.login_title),
                style = MaterialTheme.typography.headlineLarge,
                textAlign = TextAlign.Left
            )

            Spacer(Modifier.height(space32))

            if (state.errorMessage.isNotBlank()) {
                Text(
                    modifier = Modifier.fillMaxWidth(),
                    text = state.errorMessage,
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.error,
                    textAlign = TextAlign.Left
                )
            }

            LoginInputs(
                emailState = textEmailState,
                passwordState = textPassState,
                isError = state.hasLoginError && state.hasPasswordError
            )

            Spacer(Modifier.height(space20))

            Text(
                modifier = Modifier.fillMaxWidth(),
                text = stringResource(R.string.forgot_password),
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onBackground,
                textAlign = TextAlign.Right
            )

            Spacer(Modifier.height(space20))

            ButtonWithLoader(
                modifier = Modifier
                    .fillMaxWidth(),
                text = stringResource(R.string.login_button),
                onClick = { action(LoginAction.OnLogin) },
                height = 56.dp,
                isLoading = state.isLoading,
                isEnabled = isButtonEnabled
            )

            Spacer(Modifier.height(space16))

            Row() {
                Text(
                    text = stringResource(R.string.no_account_prompt) + " ",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onBackground
                )

                Text(
                    modifier = Modifier
                        .clickable {
                            action(LoginAction.OnNoAccount)
                        },
                    text = stringResource(R.string.register_button),
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
    }
}

@Preview
@Composable
private fun Preview() {
    JustChatttiClientTheme() {
        LoginContent(
            state = LoginState(),
            action = {}
        )
    }
}
