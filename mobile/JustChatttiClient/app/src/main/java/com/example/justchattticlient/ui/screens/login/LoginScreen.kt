package com.example.justchattticlient.ui.screens.login


import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.VerticalDivider
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import com.example.justchattticlient.ui.theme.DTTextFieldBorder
import com.example.justchattticlient.R
import com.example.justchattticlient.data.LoginResult
import com.example.justchattticlient.navigation.Screen
import com.example.justchattticlient.ui.components.AuthTextField

@Composable
fun LoginScreen(navController: NavHostController) {
    val authViewModel: AuthViewModel = viewModel()
    var loginText by remember { mutableStateOf("") }
    var passwordText by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    val result = authViewModel.loginResult
    Scaffold(
            modifier = Modifier.fillMaxSize(),
            containerColor = MaterialTheme.colorScheme.background
        ) { innerPadding ->

        Box(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .padding(horizontal = 30.dp)
        ) {
            Column(
                modifier = Modifier.matchParentSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {

                Box(Modifier.fillMaxWidth()) {
                    Text(
                        text = "Вход\nв аккаунт",
                        color = MaterialTheme.colorScheme.onBackground,
                        fontSize = 47.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                VerticalDivider(Modifier.height(40.dp), color = Color.Transparent)

                AuthTextField(
                    value = loginText,
                    onValueChange = { loginText = it },
                    placeholder = "Имя пользователя",
                    leadingIconId = R.drawable.user_icon
                )

                Spacer(Modifier.height(15.dp))


                AuthTextField(
                    value = passwordText,
                    onValueChange = { passwordText = it },
                    placeholder = "Пароль",
                    leadingIconId = R.drawable.lock_icon,
                    isPassword = true,
                    passwordVisible = passwordVisible,
                    onVisibilityClick = { passwordVisible = !passwordVisible }
                )

                VerticalDivider(Modifier.height(15.dp), color = Color.Transparent)

                Text(
                    modifier = Modifier.align(Alignment.End),
                    text = "Забыли пароль?",
                    color = DTTextFieldBorder,
                )

                VerticalDivider(Modifier.height(15.dp), color = Color.Transparent)

                Button(
                    onClick = { authViewModel.doLogin(loginText, passwordText) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(60.dp),
                    shape = RoundedCornerShape(13.dp),
                )
                {
                    Text("Вход", color = Color.White, fontSize = 18.sp)
                }

                VerticalDivider(Modifier.height(15.dp), color = Color.Transparent)

                Row() {
                    Text(text = "Первый раз у нас? ", color = DTTextFieldBorder)
                    Text(
                        text = "Регистрация", fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.clickable {
                            navController.navigate(Screen.Registration)
                        })
                }

                if (result != null) {
                    LaunchedEffect(result) {
                        if (result is LoginResult.Success) {
                            android.util.Log.d("AUTH_DEBUG", "Access Token: ${result.access_token}")
                            android.util.Log.d("AUTH_DEBUG", "Refresh Token: ${result.refresh_token}")

                            navController.navigate(Screen.Chats)
                        }
                    }

                    val errorMessage = when (result) {
                        is LoginResult.Error400 -> result.detail
                        is LoginResult.Error422 -> result.detail.firstOrNull()?.msg ?: "Ошибка валидации"
                        is LoginResult.Error500 -> result.detail
                        is LoginResult.Success -> null
                        else -> null
                    }

                    errorMessage?.let {
                        Text(text = it, color = Color.Red, modifier = Modifier.padding(top = 10.dp))
                    }
                }
            }
        }

    }
}





