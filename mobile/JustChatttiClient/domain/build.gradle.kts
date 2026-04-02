plugins {
    id("common-convention")
}

androidConfig {}

dependencies {
    implementation(project(":data"))
    implementation(project(":core:common"))
}