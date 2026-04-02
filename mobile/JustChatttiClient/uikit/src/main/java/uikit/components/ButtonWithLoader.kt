package uikit.components

import androidx.annotation.DrawableRes
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import uikit.SmallBoxShape
import uikit.space10
import uikit.space48
import uikit.theme.JustChatttiClientTheme

@Composable
fun ButtonWithLoader(
    text: String,
    modifier: Modifier = Modifier,
    isEnabled: Boolean = true,
    isLoading: Boolean = false,
    color: Color = MaterialTheme.colorScheme.primary,
    height: Dp = 40.dp,
    contentPadding: PaddingValues = ButtonDefaults.ContentPadding,
    shape: Shape = SmallBoxShape,
    onClick: () -> Unit
) {
    if (isLoading) {
        Box(
            modifier = Modifier
                .then(modifier)
                .fillMaxWidth()
                .height(height)
                .clip(RoundedCornerShape(space10))
                .background(color)
        ) {
            CircularProgressIndicator(
                color = MaterialTheme.colorScheme.onPrimary,
                strokeWidth = 3.dp,
                modifier = Modifier
                    .size(height / 2)
                    .align(Alignment.Center)
            )
        }
    } else {
        DefaultButton(
            text = text,
            modifier = modifier,
            isEnabled = isEnabled,
            color = color,
            height = height,
            contentPadding = contentPadding,
            shape = shape,
            onClick = onClick
        )
    }
}

@Preview
@Composable
private fun Preview() {
    JustChatttiClientTheme() {
        ButtonWithLoader(
            text = "text",
            isLoading = true
        ) { }
    }
}