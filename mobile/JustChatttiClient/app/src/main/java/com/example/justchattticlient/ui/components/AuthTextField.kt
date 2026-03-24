package com.example.justchattticlient.ui.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Visibility
import androidx.compose.material.icons.outlined.VisibilityOff
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.example.justchattticlient.ui.theme.DTTextFieldBg
import com.example.justchattticlient.ui.theme.DTTextFieldBorder

@Composable
fun AuthTextField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    leadingIconId: Int,
    isPassword: Boolean = false,
    passwordVisible: Boolean = false,
    onVisibilityClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier
            .fillMaxWidth()
            .height(60.dp),
        shape = RoundedCornerShape(13.dp),
        visualTransformation = if (isPassword && !passwordVisible) PasswordVisualTransformation() else VisualTransformation.None,
        keyboardOptions = if (isPassword) KeyboardOptions(keyboardType = KeyboardType.Password) else KeyboardOptions.Default,
        placeholder = {
            Text(placeholder, color = DTTextFieldBorder)
        },
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = DTTextFieldBg,
            unfocusedContainerColor = DTTextFieldBg,
            focusedBorderColor = DTTextFieldBorder,
            unfocusedBorderColor = Color.Transparent,
            focusedTextColor = Color.White,
            unfocusedTextColor = Color.White,
            cursorColor = DTTextFieldBorder
        ),
        singleLine = true,
        leadingIcon = {
            Icon(
                painter = painterResource(id = leadingIconId),
                contentDescription = null,
                tint = DTTextFieldBorder,
                modifier = Modifier.size(24.dp)
            )
        },
        trailingIcon = if (isPassword && onVisibilityClick != null) {
            {
                IconButton(onClick = onVisibilityClick) {
                    Icon(
                        imageVector = if (passwordVisible) Icons.Outlined.Visibility else Icons.Outlined.VisibilityOff,
                        contentDescription = null,
                        tint = DTTextFieldBorder.copy(alpha = 0.8f)
                    )
                }
            }
        } else null
    )
}
