plugins {
    id("common-convention")
}

androidConfig {
}

dependencies {
    implementation(libs.androidx.navigation.compose)
    implementation(project(":core:common"))
}