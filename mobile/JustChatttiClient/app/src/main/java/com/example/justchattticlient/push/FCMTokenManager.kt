package com.example.justchattticlient.push

import android.content.Context
import com.example.justchattticlient.network.NetworkClient
import com.example.justchattticlient.network.FCMService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import retrofit2.HttpException

object FCMTokenManager {
    private const val PREFS_NAME = "fcm_prefs"
    private const val KEY_TOKEN_SENT = "token_sent_to_server"

    fun registerToken(context: Context, token: String) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        if (prefs.getBoolean(KEY_TOKEN_SENT, false)) return

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val service = NetworkClient.apiRetrofit.create(FCMService::class.java)
                val response = service.registerToken(FCMRegisterRequest(token, null))
                if (response.isSuccessful) {
                    prefs.edit().putBoolean(KEY_TOKEN_SENT, true).apply()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun unregisterToken(context: Context, token: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val service = NetworkClient.apiRetrofit.create(FCMService::class.java)
                service.unregisterToken(FCMUnregisterRequest(token))
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                    .edit().remove(KEY_TOKEN_SENT).apply()
            }
        }
    }
}