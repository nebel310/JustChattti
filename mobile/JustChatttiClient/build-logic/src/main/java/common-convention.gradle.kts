plugins {
    id("com.android.library")
}

androidConfig()

dependencies {
    implementation(platform(libs.koin.bom))

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)

    implementation(libs.koin.core)
    implementation(libs.koin.android)
}