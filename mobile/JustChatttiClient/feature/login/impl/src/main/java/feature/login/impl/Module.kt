package feature.login.impl

import org.koin.core.module.dsl.viewModelOf
import org.koin.dsl.module

val loginImplModule = module {
    viewModelOf(::LoginViewModel)
}