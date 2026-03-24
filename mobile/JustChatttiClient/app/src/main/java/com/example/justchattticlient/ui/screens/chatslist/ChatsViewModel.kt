import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import com.example.justchattticlient.data.ChatListItemResponse
import com.example.justchattticlient.network.ChatListRepository
import kotlinx.coroutines.flow.asStateFlow

class ChatsViewModel(
    private val repository: ChatListRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    var searchQuery = MutableStateFlow("")

    init {
        loadChats()
    }

    fun loadChats() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            val result = repository.getChats()

            _uiState.value = when {
                result.isSuccess -> UiState.Success(result.getOrNull() ?: emptyList())
                else -> UiState.Error(result.exceptionOrNull()?.message ?: "Ошибка загрузки")
            }
        }
    }

    fun updateSearch(query: String) {
        searchQuery.value = query
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val chats: List<ChatListItemResponse>) : UiState()
    data class Error(val message: String) : UiState()
}
