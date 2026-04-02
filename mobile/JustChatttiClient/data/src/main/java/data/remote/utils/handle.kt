package data.remote.utils

import com.google.gson.JsonParser
import core.common.exceptions.NetworkError
import core.common.exceptions.NetworkException
import retrofit2.Response

internal fun <T, R>Response<T>.handle(configure: (HandleContext<T, R>.() -> Unit)? = null): R {
    val context = HandleContext<T, R>(this)
    configure?.let { context.it() }
    return context.execute()
}

internal class HandleContext<T, R>(
    private val response: Response<T>
){
    private val processors = mutableMapOf<Int, (T?) -> R>()
    private var transformer: ((T) -> R)? = null

    fun process(code: Int, handler: (T?) -> R) {
        processors[code] = handler
    }

    fun transformSuccess(handler: (T) -> R){
        transformer = handler
    }

    internal fun execute(): R {
        val statusCode = response.code()
        val body = response.body()

        processors[statusCode]?.invoke(body)?.let {
            return it
        }

        return handleDefaults(statusCode, body)
    }

    @Suppress("UNCHECKED_CAST")
    private fun handleDefaults(statusCode: Int, body: T?): R {
        if (statusCode in 200..399) {
            return body?.let { responseBody ->
                (transformer?.invoke(responseBody) ?: responseBody) as R
            } ?: throw NetworkException(
                error = NetworkError(status = 0)
            )
        }

        val errorJson = response.errorBody()?.string()

        val errorMessage = try {
            val jsonObject = JsonParser.parseString(errorJson).asJsonObject
            jsonObject.get("detail")?.asString ?: "Unknown Error"
        } catch (e: Exception) {
            "Unknown Error"
        }

        throw NetworkException(
            error = NetworkError(
                status = statusCode,
                title = errorMessage
            )
        )
    }
}