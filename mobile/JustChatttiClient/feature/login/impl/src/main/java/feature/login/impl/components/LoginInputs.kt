package feature.login.impl.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.input.KeyboardActionHandler
import androidx.compose.foundation.text.input.TextFieldState
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusDirection
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.justchattticlient.uikit.R
import uikit.components.PasswordInput
import uikit.components.TextInput
import uikit.space16
import uikit.theme.JustChatttiClientTheme

@Composable
internal fun LoginInputs(
    emailState: TextFieldState,
    passwordState: TextFieldState,
    modifier: Modifier = Modifier,
    heightInput: Dp = 56.dp,
    isError: Boolean = false
) {
    val focusRequester = remember {
        FocusRequester()
    }
    val focusManager = LocalFocusManager.current

    Column(
        modifier = modifier
            .fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(space16)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(space16)
        ) {
            TextInput(
                modifier = Modifier
                    .height(heightInput)
                    .focusRequester(focusRequester),
                state = emailState,
                placeholder = stringResource(R.string.username_hint),
                contentPadding = PaddingValues(
                    vertical = 16.dp,
                    horizontal = 16.dp
                ),
                keyboardOptions = KeyboardOptions(
                    imeAction = ImeAction.Next
                ),
                onKeyboardAction = KeyboardActionHandler {
                    focusManager.moveFocus(FocusDirection.Down)
                },
                leadingIcon = {
                    Icon(
                        painter = painterResource(R.drawable.user_icon),
                        contentDescription = null
                    )
                },
                isError = isError
            )

            PasswordInput(
                state = passwordState,
                placeholder = stringResource(R.string.password_hint),
                modifier = Modifier.height(heightInput),
                contentPadding = PaddingValues(
                    vertical = 16.dp,
                    horizontal = 16.dp
                ),
                keyboardOptions = KeyboardOptions(
                    imeAction = ImeAction.Done
                ),
                onKeyboardAction = KeyboardActionHandler {
                    focusManager.clearFocus()
                },
                leadingIcon = {
                    Icon(
                        painter = painterResource(R.drawable.lock_icon),
                        contentDescription = null
                    )
                },
                isError = isError
            )
        }
    }
}

@Preview
@Composable
private fun Preview() {
    JustChatttiClientTheme() {
        LoginInputs(
            emailState = rememberTextFieldState(),
            passwordState = rememberTextFieldState(),
            isError = true
        )
    }
}