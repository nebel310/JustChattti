package uikit.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.Shape

@Composable
fun BlurBox(
    modifier: Modifier = Modifier,
    contentAlignment: Alignment = Alignment.TopStart,
    radius: Int = 15,
    containerColor: Color = MaterialTheme.colorScheme.secondaryContainer,
    shape: Shape = RectangleShape,
    content: @Composable BoxScope.() -> Unit,
) {
    Box(
        modifier = modifier
            .clip(shape)
            .background(Color.Transparent),
        contentAlignment = contentAlignment
    ) {

        Box(
            modifier = Modifier
                .matchParentSize()
                .background(
                    color = containerColor.copy(alpha = 0.7f),
                    shape = shape
                ),
        )

        content()
    }
}
