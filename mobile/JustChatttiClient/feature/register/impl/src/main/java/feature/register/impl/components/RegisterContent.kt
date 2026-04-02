package feature.register.impl.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.justchattticlient.uikit.R
import feature.register.impl.state.RegisterAction
import feature.register.impl.state.RegisterState
import kotlinx.coroutines.flow.collectLatest
import uikit.components.ButtonWithLoader
import uikit.components.DefaultButton
import uikit.space16
import uikit.space24
import uikit.space28
import uikit.theme.JustChatttiClientTheme

@Composable
internal fun RegisterContent(
    state: RegisterState,
    action: (RegisterAction) -> Unit
) {
    val textEmailState = rememberTextFieldState(state.login)
    val textPassState = rememberTextFieldState(state.password)
    val textPassConfirmState = rememberTextFieldState(state.passwordConfirm)
    val isButtonEnabled = remember {
        textEmailState.text.isNotBlank() &&
                textPassState.text.isNotBlank() &&
                textPassConfirmState.text.isNotBlank() &&
                textPassState.text != textPassConfirmState.text
    }

    LaunchedEffect(Unit) {
        snapshotFlow { textEmailState.text }
            .collectLatest {
                action(RegisterAction.ChangeLogin(it.toString()))
            }
    }

    LaunchedEffect(Unit) {
        snapshotFlow { textPassState.text }
            .collectLatest {
                action(RegisterAction.ChangePassword(it.toString()))
            }
    }

    LaunchedEffect(Unit) {
        snapshotFlow { textPassConfirmState.text }
            .collectLatest {
                action(RegisterAction.ChangePasswordConfirm(it.toString()))
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
                text = stringResource(R.string.register_title),
                style = MaterialTheme.typography.headlineLarge,
                textAlign = TextAlign.Left
            )

            Spacer(Modifier.height(space28))

            if (state.errorMessage.isNotBlank()) {
                Text(
                    modifier = Modifier.fillMaxWidth(),
                    text = state.errorMessage,
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.error,
                    textAlign = TextAlign.Left
                )
            }
            RegisterInputs(
                emailState = textEmailState,
                passwordState = textPassState,
                passwordStateConfirm = textPassConfirmState,
                isError = state.hasErrors
            )

            Spacer(Modifier.height(space24))

            ButtonWithLoader(
                modifier = Modifier
                    .fillMaxWidth(),
                text = stringResource(R.string.register_button),
                onClick = { action(RegisterAction.OnRegister) },
                height = 56.dp,
                isLoading = state.isLoading,
                isEnabled = isButtonEnabled
            )

            Spacer(Modifier.height(space16))

            Row() {
                Text(
                    text = stringResource(R.string.has_account_prompt) + " ",
                    style = MaterialTheme.typography.bodyLarge,
//                    color = MaterialTheme.colorScheme.onBackground
                )

                Text(
                    modifier = Modifier
                        .clickable {
                            action(RegisterAction.HasAccount)
                        },
                    text = stringResource(R.string.login_button),
                    style = MaterialTheme.typography.bodyLarge,
//                    color = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun Preview() {
    JustChatttiClientTheme() {
        RegisterContent(
            state = RegisterState(
                errorMessage = "Server error"
            ),
            action = {}
        )
    }
}