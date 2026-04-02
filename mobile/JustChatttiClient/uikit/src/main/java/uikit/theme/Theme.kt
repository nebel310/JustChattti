package uikit.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF1B1E20),
    onPrimary = Color(0xFFFFFFFF),

    secondary = Color(0xFF94979A),
    onSecondary = Color(0xFFFFFFFF),

    secondaryContainer = Color(0xFF232627),
    onSecondaryContainer = Color(0xFFFFFFFF),

    background = Color(0xFF000000),
    onBackground = Color(0xFFCBCBCB),

    surface = Color(0xFF121415),
    onSurface = Color(0xFFFFFFFF),

    surfaceVariant = Color(0xFF1A1C1E),
    onSurfaceVariant = Color(0xFFC2C3CB),

    surfaceContainer = Color(0xFF1B1E20),

    outline = Color(0xFF3C3F41),
    outlineVariant = Color(0xFF2A2F36),

    error = Color(0xFFFF4D5E),
    onError = Color(0xFFFFFFFF),

    errorContainer = Color(0xFF5C1A1F),
    onErrorContainer = Color(0xFFFFDAD6),

    inverseSurface = Color(0xFFEDEDED),
    inverseOnSurface = Color(0xFF1A1B1F),
)

private val LightColorScheme = lightColorScheme(
)

@Composable
fun JustChatttiClientTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        //TODO: поменять как светлая палитра выйдет
        else -> DarkColorScheme

    }

    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography,
        content = content
    )
}