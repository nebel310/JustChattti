plugins {
    id("feature-impl-convention")
    alias(libs.plugins.kotlin.compose)
}

androidConfig {}

dependencies {
    implementation(project(":data"))
    implementation(project(":core:storage"))
    implementation(project(":domain"))
    implementation(project(":feature:chats:api"))
    implementation(project(":feature:common"))
    implementation(project(":uikit"))
}
