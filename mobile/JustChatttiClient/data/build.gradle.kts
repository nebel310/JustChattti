plugins {
    id("common-convention")
    alias(libs.plugins.ksp)
}

androidConfig {}

dependencies {
    implementation(project(":core:common"))
    implementation(libs.gson)
    implementation(libs.converter.gson)
    implementation(libs.retrofit)
    implementation(libs.room.runtime)
    ksp(libs.room.compiler)
}
