package uikit.components

import androidx.compose.foundation.border
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.BasicSecureTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.input.KeyboardActionHandler
import androidx.compose.foundation.text.input.TextFieldState
import androidx.compose.foundation.text.input.TextObfuscationMode
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.foundation.text.selection.LocalTextSelectionColors
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldColors
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.justchattticlient.uikit.R
import uikit.MediumBoxShape
import uikit.SmallBoxShape

@Composable
fun TextInput(
    state: TextFieldState,
    modifier: Modifier = Modifier,
    placeholder: String? = null,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    onKeyboardAction: KeyboardActionHandler? = null,
    isError: Boolean = false,
    shape: Shape = SmallBoxShape,
    textStyle: TextStyle = MaterialTheme.typography.bodyMedium,
    stylePlaceholder: TextStyle = MaterialTheme.typography.bodyMedium,
    contentPadding: PaddingValues = TextFieldDefaults.contentPaddingWithoutLabel(),
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    colors: TextFieldColors = TextFieldDefaults.colors(),
) {
    OutlinedTextField(
        modifier = modifier
            .fillMaxWidth(),
        state = state,
        isError = isError,
        placeholder = {
            Text(
                text = placeholder ?: "",
                style = stylePlaceholder
            )
        },
        shape = shape,
        contentPadding = contentPadding,
        textStyle = textStyle,
        keyboardOptions = keyboardOptions,
        onKeyboardAction = onKeyboardAction,
        leadingIcon = leadingIcon,
        trailingIcon = trailingIcon,
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = colors.focusedContainerColor,
            unfocusedContainerColor = colors.unfocusedContainerColor,
            errorContainerColor = colors.errorContainerColor,
            focusedBorderColor = MaterialTheme.colorScheme.onSurfaceVariant,
            unfocusedBorderColor = Color.Transparent,
        ),

    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PasswordInput(
    state: TextFieldState,
    modifier: Modifier = Modifier,
    placeholder: String? = null,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    onKeyboardAction: KeyboardActionHandler? = null,
    isError: Boolean = false,
    shape: Shape = SmallBoxShape,
    textStyle: TextStyle = MaterialTheme.typography.bodyMedium,
    stylePlaceholder: TextStyle = MaterialTheme.typography.bodyMedium,
    contentPadding: PaddingValues = TextFieldDefaults.contentPaddingWithoutLabel(),
    colors: TextFieldColors = OutlinedTextFieldDefaults.colors(),
    leadingIcon: @Composable (() -> Unit)? = null,
) {
    var passwordVisibility by remember { mutableStateOf(false) }
    val interactionSource = remember { MutableInteractionSource() }

    val icon = if (passwordVisibility)
        painterResource(id = R.drawable.eye_opened)
    else
        painterResource(id = R.drawable.eye_closed)

    val isFocused by interactionSource.collectIsFocusedAsState()

    val targetColor = when {
        isError -> colors.errorTextColor
        isFocused -> colors.focusedTextColor
        else -> colors.unfocusedTextColor
    }
    val mergedTextStyle = textStyle.copy(color = targetColor)

    val cursorColor = if (isError) {
        colors.errorCursorColor
    } else {
        colors.cursorColor
    }

    val borderColor = when {
        isError -> MaterialTheme.colorScheme.error
        isFocused -> MaterialTheme.colorScheme.onSurfaceVariant
        else -> Color.Transparent
    }

    CompositionLocalProvider(LocalTextSelectionColors provides colors.textSelectionColors) {
        BasicSecureTextField(
            state = state,
            modifier = modifier
                .fillMaxWidth()
                .border(
                    width = 1.dp,
                    color = borderColor,
                    shape = shape
                ),
            textStyle = mergedTextStyle,
            keyboardOptions = keyboardOptions.copy(
                keyboardType = KeyboardType.Password
            ),
            onKeyboardAction = onKeyboardAction,
            interactionSource = interactionSource,
            enabled = true,
            textObfuscationMode = if (passwordVisibility) {
                TextObfuscationMode.Visible
            } else {
                TextObfuscationMode.RevealLastTyped
            },
            cursorBrush = SolidColor(cursorColor),
            decorator = { innerTextField ->
                TextFieldDefaults.DecorationBox(
                    value = state.text.toString(),
                    innerTextField = innerTextField,
                    enabled = true,
                    singleLine = true,
                    visualTransformation = if (passwordVisibility) {
                        VisualTransformation.None
                    } else PasswordVisualTransformation(),
                    interactionSource = interactionSource,
                    isError = isError,
                    placeholder = {
                        Text(
                            text = placeholder ?: "",
                            style = stylePlaceholder
                        )
                    },
                    trailingIcon = {
                        IconButton(onClick = { passwordVisibility = !passwordVisibility }) {
                            Icon(
                                painter = icon,
                                contentDescription = "Visibility Icon"
                            )
                        }
                    },
                    leadingIcon = leadingIcon,
                    shape = shape,
                    colors = TextFieldDefaults.colors(
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent,
                        disabledIndicatorColor = Color.Transparent,
                        errorIndicatorColor = Color.Transparent
                    ),
                    contentPadding = contentPadding,
                    container = {
                        TextFieldDefaults.Container(
                            enabled = true,
                            isError = isError,
                            interactionSource = interactionSource,
                            colors = TextFieldDefaults.colors(
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent,
                                disabledIndicatorColor = Color.Transparent,
                                errorIndicatorColor = Color.Transparent
                            ),
                            shape = shape,
                        )
                    }
                )
            }
        )
    }
}

@Preview(showBackground = true)
@Composable
private fun Preview() {
    Column {
        PasswordInput(
            state = rememberTextFieldState(),
            placeholder = "password input",
        )
        Spacer(Modifier.height(20.dp))
        TextInput(
            state = rememberTextFieldState(),
            placeholder = "text input",
        )
    }
}
