package feature.register.impl

import org.koin.core.module.dsl.viewModelOf
import org.koin.dsl.module

val registerImplModule = module {
    viewModelOf(::RegisterViewModel)
}