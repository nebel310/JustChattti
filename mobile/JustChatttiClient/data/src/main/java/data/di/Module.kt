package data.di


import androidx.datastore.core.DataStore
import androidx.datastore.core.DataStoreFactory
import androidx.datastore.dataStoreFile
import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import data.local.TokenManager
import data.local.TokenManagerImpl
import data.models.TokenData
import data.models.TokenDataSerializer
import data.remote.api.AuthApi
import data.remote.api.UserApi
import data.remote.utils.AccessTokenInterceptor
import data.remote.utils.TokenAuthenticator
import data.repositories.auth.AuthUserRepository
import data.repositories.auth.AuthUserRepositoryImpl
import data.repositories.user.UsersRepository
import data.repositories.user.UsersRepositoryImpl
import okhttp3.OkHttpClient
import org.koin.android.ext.koin.androidContext
import org.koin.dsl.module
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.create

val dataModule = module {
    single<DataStore<TokenData>> {
        DataStoreFactory.create(
            serializer = TokenDataSerializer,
            produceFile = { androidContext().dataStoreFile("tokens.json") }
        )
    }

    single<TokenManager> {
        TokenManagerImpl(get())
    }

    single { TokenAuthenticator(get(), get()) }
    single { AccessTokenInterceptor(get()) }

    single {
        OkHttpClient.Builder()
            .addInterceptor(get<AccessTokenInterceptor>())
            .authenticator(get<TokenAuthenticator>())
            .build()
    }

    single<AuthApi> {
        Retrofit.Builder()
            .baseUrl("http://10.0.2.2:1000/auth/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create()
    }

    single<AuthUserRepository> {
        AuthUserRepositoryImpl(get(), get())
    }

    single<UserApi> {
        Retrofit.Builder()
            .baseUrl("http://10.0.2.2:1000/auth/")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get())
            .build()
            .create()
    }

    single<UsersRepository> {
        UsersRepositoryImpl(get(), get())
    }
}