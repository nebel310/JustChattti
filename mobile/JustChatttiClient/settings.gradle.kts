pluginManagement {
    includeBuild("build-logic")

    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "JustChattti Client"

include(":app")

include(":core:common")
include(":core:navigation")
include(":core:storage")

include(":domain")

include(":data")

include(":feature:common")

include(":feature:register:api")
include(":feature:register:impl")

include(":feature:login:api")
include(":feature:login:impl")

include(":feature:chats:api")
include(":feature:chats:impl")

include(":uikit")
