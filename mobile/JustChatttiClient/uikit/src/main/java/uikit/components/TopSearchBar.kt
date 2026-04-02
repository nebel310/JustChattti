package uikit.components

import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.DockedSearchBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SearchBarDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.PlatformTextStyle
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.justchattticlient.uikit.R
import uikit.theme.JustChatttiClientTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopSearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    onSearch: (String) -> Unit,
    expanded: Boolean,
    onExpandedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    searchShape: Shape = RectangleShape,
    textFieldShape: Shape = CircleShape,
    textFieldPadding: PaddingValues = PaddingValues(0.dp),
    content: @Composable (ColumnScope.() -> Unit),
) {
    val customStyle = MaterialTheme.typography.bodyLarge.copy(
        platformStyle = PlatformTextStyle(includeFontPadding = false)
    )

    DockedSearchBar(
        modifier = modifier,
        expanded = expanded,
        onExpandedChange = onExpandedChange,
        shape = searchShape,
        tonalElevation = 0.dp,
        colors = SearchBarDefaults.colors(
            containerColor = Color.Transparent,
            inputFieldColors = SearchBarDefaults.inputFieldColors(
                focusedTextColor = MaterialTheme.colorScheme.onSurface,
                unfocusedTextColor = MaterialTheme.colorScheme.onSurface
            )
        ),
        inputField = {
            CompositionLocalProvider(LocalTextStyle provides customStyle) {
                SearchBarDefaults.InputField(
                    modifier = Modifier
                        .padding(textFieldPadding)
                        .clip(textFieldShape)
                        .height(40.dp),
                    query = query,
                    onQueryChange = onQueryChange,
                    onSearch = onSearch,
                    expanded = expanded,
                    onExpandedChange = onExpandedChange,
                    placeholder = {
                        Text(
                            text = stringResource(R.string.search_hint),
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            style = MaterialTheme.typography.labelLarge
                        )
                    },
                    leadingIcon = leadingIcon,
                    trailingIcon = trailingIcon,
                    colors = TextFieldDefaults.colors(
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent,
                        unfocusedContainerColor = MaterialTheme.colorScheme.surfaceContainer,
                        focusedContainerColor = MaterialTheme.colorScheme.surfaceContainer
                    )
                )
            }
        }
    ) {
        content()
    }
}

@Preview
@Composable
private fun Preview() {
    JustChatttiClientTheme(darkTheme = true) {
        TopSearchBar(
            query = "",
            onQueryChange = {},
            onSearch = {},
            expanded = false,
            onExpandedChange = {}
        ) {}
    }
}