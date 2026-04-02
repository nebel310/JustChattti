package com.example.justchattticlient.di

import data.di.dataModule
import domain.di.domainModule
import feature.register.impl.registerImplModule
import org.koin.dsl.module

val rootModule = module {
    includes(
        dataModule
    )

    includes(
        domainModule
    )

    includes(
        registerImplModule
    )
}