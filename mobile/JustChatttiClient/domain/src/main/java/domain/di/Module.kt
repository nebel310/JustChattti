package domain.di

import domain.auth.LoginUseCase
import domain.account.LogoutUseCase
import domain.auth.RegisterUseCase
import org.koin.core.module.dsl.factoryOf
import org.koin.dsl.module

val domainModule = module {
    factoryOf(::LoginUseCase)
    factoryOf(::RegisterUseCase)
    factoryOf(::LogoutUseCase)
}