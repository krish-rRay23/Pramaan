package com.pramaan.demo.network

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path

interface ApiService {

    @GET("ping")
    suspend fun ping(): Response<Map<String, Any>>

    @GET("account/{loanId}")
    suspend fun getAccount(@Path("loanId") loanId: String): Response<Account>

    @GET("intent/latest/{customerId}")
    suspend fun latestIntent(@Path("customerId") customerId: String): Response<SignedIntent>

    @POST("intent/verify")
    suspend fun verifyIntent(@Body request: VerifyRequest): Response<VerifyResponse>

    @POST("intent/kill-switch")
    suspend fun killSwitch(@Body request: CustomerKillSwitchRequest): Response<CustomerKillSwitchResponse>

    @GET("receipts/customer/{customerId}")
    suspend fun getCustomerReceipts(@Path("customerId") customerId: String): Response<List<TrustReceipt>>

    @GET("receipt/{receiptId}")
    suspend fun getReceipt(@Path("receiptId") receiptId: String): Response<TrustReceipt>

    @GET("receipts/verify/{receiptId}")
    suspend fun verifyPublicReceipt(@Path("receiptId") receiptId: String): Response<PublicReceiptVerification>

    @Multipart
    @POST("kyc/authenticity")
    suspend fun kycAuthenticity(@Part file: MultipartBody.Part): Response<AuthenticityResponse>

    @POST("demo/reset")
    suspend fun resetDemo(): Response<ResetResponse>
}
