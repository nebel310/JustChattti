plugins {
    id("common-convention")
    id("compose-convention")
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlinx.serialization)
}

androidConfig {}

dependencies {
    implementation(libs.kotlinx.serialization)
    api(project(":core:common"))
    api(project(":core:navigation"))
}
