plugins {
    id("feature-api-convention")
    alias(libs.plugins.kotlinx.serialization)
}

androidConfig {}

dependencies {
    api(project(":feature:common"))
    implementation(libs.kotlinx.serialization)
}
