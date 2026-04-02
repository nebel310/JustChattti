package data.local

import androidx.datastore.core.DataStore
import data.models.TokenData
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.runBlocking


class TokenManagerImpl(
    private val dataStore: DataStore<TokenData>
) : TokenManager {
    override suspend fun getAccessToken(): String? {
        return dataStore.data.firstOrNull()?.accessToken
    }

    override fun getAccessTokenBlocking(): String? {
        return runBlocking {
            dataStore.data.firstOrNull()?.accessToken
        }
    }

    override suspend fun setAccessToken(token: String) {
        dataStore.updateData {
            it.copy(
                accessToken = token
            )
        }
    }

    override suspend fun getRefreshToken(): String? {
        return dataStore.data.firstOrNull()?.refreshToken
    }

    override suspend fun setRefreshToken(token: String) {
        dataStore.updateData {
            it.copy(
                refreshToken = token
            )
        }
    }

    override suspend fun getUserId(): Int? {
        return dataStore.data.firstOrNull()?.userId
    }

    override suspend fun setUserId(value: Int) {
        dataStore.updateData {
            it.copy(
                userId = value
            )
        }
    }

    override suspend fun clear() {
        dataStore.updateData { TokenData() }
    }
}