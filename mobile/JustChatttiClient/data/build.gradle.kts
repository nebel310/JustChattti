plugins {
    id("common-convention")
    alias(libs.plugins.ksp)
    alias(libs.plugins.kotlinx.serialization)
}

androidConfig {}

dependencies {
    implementation(project(":core:common"))
    implementation(project(":core:storage"))
    implementation(libs.kotlinx.serialization)
    implementation(libs.gson)
    implementation(libs.converter.gson)
    implementation(libs.retrofit)
    implementation(libs.room.runtime)
    ksp(libs.room.compiler)
    implementation(libs.androidx.datastore.preferences)
    implementation(libs.kotlinx.datetime)
}
