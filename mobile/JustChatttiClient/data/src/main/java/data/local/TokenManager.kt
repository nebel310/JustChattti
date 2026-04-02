package data.local

interface TokenManager {
    suspend fun getAccessToken(): String?
    fun getAccessTokenBlocking(): String?
    suspend fun setAccessToken(token: String): Unit
    suspend fun getRefreshToken(): String?
    suspend fun setRefreshToken(token: String): Unit
    suspend fun getUserId(): Int?
    suspend fun setUserId(value: Int)
    suspend fun clear(): Unit
}