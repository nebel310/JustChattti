package com.example.justchattticlient

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.compose.rememberNavController
import com.example.justchattticlient.navigation.AppNavHost
import com.example.justchattticlient.network.NetworkClient
import com.example.justchattticlient.ui.theme.JustChatttiClientTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        NetworkClient.init(this)
        setContent {
            JustChatttiClientTheme {
                val navController = rememberNavController()
                AppNavHost(navController = navController)
            }
        }
    }
}

