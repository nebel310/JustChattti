package com.example.justchattticlient.network

import AuthInterceptor
import TokenManager
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import android.content.Context
import okhttp3.OkHttpClient


object NetworkClient {
    private const val BASE_URL = "http://10.0.2.2:1000/"
    private lateinit var tokenManager: TokenManager

    fun init(context: Context) {
        tokenManager = TokenManager(context)
    }

    private val publicClient = OkHttpClient.Builder().build()

    private val authenticatedClient by lazy {
        if (::tokenManager.isInitialized) {
            OkHttpClient.Builder()
                .addInterceptor(AuthInterceptor(tokenManager))
                .build()
        } else {
            publicClient
        }
    }

    val authRetrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(publicClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val apiRetrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(authenticatedClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

