package uikit.components

import android.content.res.Configuration
import androidx.annotation.DrawableRes
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import uikit.SmallBoxShape
import uikit.theme.JustChatttiClientTheme


@Composable
fun DefaultButton(
    text: String,
    modifier: Modifier = Modifier,
    @DrawableRes iconRes: Int? = null,
    isEnabled: Boolean = true,
    color: Color = MaterialTheme.colorScheme.primary,
    gradientBrush: Brush? = null,
    height: Dp = 40.dp,
    contentPadding: PaddingValues = ButtonDefaults.ContentPadding,
    shape: Shape = SmallBoxShape,
    onClick: () -> Unit
) {
    val buttonColors = if (gradientBrush == null) {
        ButtonDefaults.buttonColors(
            disabledContainerColor = MaterialTheme.colorScheme.surfaceContainerHighest,
            containerColor = color,
        )
    } else {
        ButtonDefaults.buttonColors(
            disabledContainerColor = Color.Transparent,
            containerColor = Color.Transparent,
        )
    }

    Button(
        onClick = onClick,
        shape = shape,
        contentPadding = contentPadding,
        modifier = modifier
            .background(
                brush = gradientBrush ?: SolidColor(color),
                shape = shape
            )
            .height(height),
        colors = buttonColors,
        enabled = isEnabled,
    ) {
        iconRes?.let {
            Icon(
                painter = painterResource(it),
                contentDescription = null,
            )
        }
        Text(
            overflow = TextOverflow.Ellipsis,
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium,
            maxLines = 1,
            text = text,
            style = MaterialTheme.typography.labelMedium
        )
    }
}

@Preview(uiMode = Configuration.UI_MODE_NIGHT_NO)
@Preview(uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun PreviewDefaultButton() {
    JustChatttiClientTheme {
        Column {
            DefaultButton(
                text = "Text",
                onClick = {},
                isEnabled = true,
                modifier = Modifier.fillMaxWidth()
            )

            DefaultButton(
                text = "Text",
                onClick = {},
                isEnabled = false,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}