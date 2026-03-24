package com.example.justchattticlient.data

import android.content.Context

class TokenManager(context: Context) {
    private val prefs = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)

    fun saveTokens(at: String, rt: String) {  // ← убрал userId
        prefs.edit()
            .putString("at", at)
            .putString("rt", rt)
            .apply()
    }

    fun getAccessToken(): String? = prefs.getString("at", null)
    fun getRefreshToken(): String? = prefs.getString("rt", null)
    fun clearTokens() {
        prefs.edit().clear().apply()
    }
}

