package com.pramaan.demo

import android.util.Base64
import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pramaan.demo.network.Account
import com.pramaan.demo.network.ApiClient
import com.pramaan.demo.network.AuthenticityResponse
import com.pramaan.demo.network.ClaimedRequest
import com.pramaan.demo.network.CustomerKillSwitchRequest
import com.pramaan.demo.network.CustomerKillSwitchResponse
import com.pramaan.demo.network.IntentPayload
import com.pramaan.demo.network.PublicReceiptVerification
import com.pramaan.demo.network.SignedIntent
import com.pramaan.demo.network.TrustReceipt
import com.pramaan.demo.network.VerifyRequest
import com.pramaan.demo.network.VerifyResponse
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.util.UUID

const val DEMO_LOAN_ID = "LOAN-4521"
const val DEMO_CUSTOMER_ID = "CUST-001"

class PramaanViewModel : ViewModel() {

    var account by mutableStateOf<Account?>(null)
        private set

    var activeIntent by mutableStateOf<SignedIntent?>(null)
        private set

    var lastVerifyResponse by mutableStateOf<VerifyResponse?>(null)
        private set

    var lastReceipt by mutableStateOf<TrustReceipt?>(null)
        private set

    var lastKillSwitchResponse by mutableStateOf<CustomerKillSwitchResponse?>(null)
        private set

    var receiptsHistory by mutableStateOf<List<TrustReceipt>>(emptyList())
        private set

    var publicVerificationResult by mutableStateOf<PublicReceiptVerification?>(null)
        private set

    var authenticityResult by mutableStateOf<AuthenticityResponse?>(null)
        private set

    var isLoading by mutableStateOf(false)
        private set

    var errorMessage by mutableStateOf<String?>(null)
        private set

    // Rural / Accessibility (Assisted Mode) State
    var isRuralMode by mutableStateOf(false)
        private set

    var ruralLanguage by mutableStateOf("HI") // "HI" (Hindi) or "EN" (English)
        private set

    // Channel origin for the current interaction (e.g. WhatsApp, Call, SMS, Agent)
    var incomingChannel by mutableStateOf("whatsapp")
        private set

    var deepLinkHandled by mutableStateOf(false)
        private set

    var pendingNavigation by mutableStateOf<String?>(null)

    fun clearPendingNavigation() {
        pendingNavigation = null
    }

    private val resolvedTokens = mutableSetOf<String>()

    var showIntentPopup by mutableStateOf(false)

    fun dismissIntentPopup() {
        showIntentPopup = false
    }

    private val moshi: Moshi by lazy {
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    init {
        loadCustomerAccount()
        checkForIncomingInteraction()
        loadReceiptHistory()
    }

    fun clearError() {
        errorMessage = null
    }

    fun toggleRuralMode() {
        isRuralMode = !isRuralMode
    }

    fun setRuralLang(lang: String) {
        ruralLanguage = lang
    }

    fun setChannelOrigin(channel: String) {
        incomingChannel = channel
    }

    fun loadCustomerAccount() = launchSafely {
        val loanId = account?.loanId ?: DEMO_LOAN_ID
        val res = ApiClient.service.getAccount(loanId)
        if (res.isSuccessful) {
            account = res.body()
        } else {
            errorMessage = "Could not synchronize account record (${res.code()})"
        }
    }

    /** Checks if TVS Credit has dispatched a genuine contact capability to this customer. */
    fun checkForIncomingInteraction(onFound: (() -> Unit)? = null) = launchSafely {
        val customerId = account?.customerId ?: DEMO_CUSTOMER_ID
        val res = ApiClient.service.latestIntent(customerId)
        if (res.isSuccessful && res.body() != null) {
            val newIntent = res.body()!!
            if (!resolvedTokens.contains(newIntent.token)) {
                if (activeIntent?.token != newIntent.token) {
                    showIntentPopup = true
                }
                activeIntent = newIntent
                onFound?.invoke()
            } else {
                if (activeIntent?.token == newIntent.token) {
                    activeIntent = null
                }
                showIntentPopup = false
            }
        } else if (res.code() == 404) {
            // Only clear activeIntent if it was not populated via an active deep link
            if (!deepLinkHandled) {
                activeIntent = null
            }
            showIntentPopup = false
        } else {
            errorMessage = "Security shield check error (${res.code()})"
        }
    }

    /**
     * Exact Action Gate: Evaluates claimed interaction against cryptographic token.
     * Evaluates exact destination, amount, and scope.
     */
    fun verifyExactAction(
        claimedDestination: String?,
        deviceConfirmed: Boolean = false,
        onComplete: (isAllowed: Boolean, isStepUp: Boolean) -> Unit,
    ) = launchSafely {
        val intent = activeIntent
        if (intent == null) {
            lastVerifyResponse = VerifyResponse(
                matched = false,
                decision = "BLOCKED",
                reason = "Unable to verify. Do not proceed.",
                signatureValid = false,
                fresh = false,
                agentAuthorized = false,
                destinationVerified = false,
                assuranceLevel = "CRITICAL",
                policyVersion = "3.2.0",
                reasonCode = "POL_NO_ACTIVE_INTENT_FAIL_CLOSED",
            )
            errorMessage = "Unable to verify. Do not proceed."
            onComplete(false, false)
            return@launchSafely
        }

        val correlationId = "CORR-${UUID.randomUUID().toString().take(8).uppercase()}"

        val request = VerifyRequest(
            token = intent.token,
            claimed = ClaimedRequest(
                loanId = intent.payload.loanId,
                purpose = intent.payload.purpose,
                amount = intent.payload.claimedAmount ?: intent.payload.amount,
                action = intent.payload.action,
                destination = claimedDestination,
                agentId = intent.payload.claimedAgentId ?: intent.payload.agentId,
                deviceConfirmed = deviceConfirmed,
            ),
            correlationId = correlationId,
            idempotent = false,
        )

        try {
            val res = ApiClient.service.verifyIntent(request)
            if (res.isSuccessful && res.body() != null) {
                val verifyBody = res.body()!!
                lastVerifyResponse = verifyBody
                if (verifyBody.trustReceipt != null) {
                    lastReceipt = verifyBody.trustReceipt
                }
                val isStepUp = verifyBody.decision == "STEP_UP_REQUIRED"
                val isAllowed = verifyBody.decision == "ALLOWED"
                if (!isStepUp) {
                    intent.token.let { resolvedTokens.add(it) }
                    activeIntent = null
                    showIntentPopup = false
                }
                onComplete(isAllowed, isStepUp)
            } else {
                intent.token.let { resolvedTokens.add(it) }
                activeIntent = null
                showIntentPopup = false
                lastVerifyResponse = VerifyResponse(
                    matched = false,
                    decision = "BLOCKED",
                    reason = "Unable to verify. Do not proceed.",
                    signatureValid = false,
                    fresh = false,
                    agentAuthorized = false,
                    destinationVerified = false,
                    assuranceLevel = "CRITICAL",
                    policyVersion = "3.2.0",
                    reasonCode = "POL_GATE_UNAVAILABLE_FAIL_CLOSED",
                    correlationId = correlationId,
                )
                errorMessage = "Unable to verify. Do not proceed."
                onComplete(false, false)
            }
        } catch (e: Exception) {
            Log.e("PramaanViewModel", "Network error during verification", e)
            intent.token.let { resolvedTokens.add(it) }
            activeIntent = null
            showIntentPopup = false
            lastVerifyResponse = VerifyResponse(
                matched = false,
                decision = "BLOCKED",
                reason = "Unable to verify. Do not proceed.",
                signatureValid = false,
                fresh = false,
                agentAuthorized = false,
                destinationVerified = false,
                assuranceLevel = "CRITICAL",
                policyVersion = "3.2.0",
                reasonCode = "POL_NETWORK_TIMEOUT_FAIL_CLOSED",
                correlationId = correlationId,
            )
            errorMessage = "Unable to verify. Do not proceed."
            onComplete(false, false)
        }
    }

    /**
     * Customer Protection Kill Switch:
     * On tap "I DON'T TRUST THIS REQUEST":
     * - Cancels pending authorization
     * - Revokes interaction
     * - Flags destination
     * - Creates fraud incident
     * - Generates Trust Receipt
     */
    fun triggerKillSwitch(
        reportedDestination: String? = null,
        reason: String = "Customer marked: I DON'T TRUST THIS REQUEST",
        onComplete: ((success: Boolean) -> Unit)? = null
    ) = launchSafely {
        val intent = activeIntent
        val loanId = intent?.payload?.loanId ?: account?.loanId ?: DEMO_LOAN_ID
        val customerId = intent?.payload?.customerId ?: account?.customerId ?: DEMO_CUSTOMER_ID

        val authVpa = account?.authorizedDestination ?: "tvscredit.collections@upi"
        val destToReport = if (reportedDestination != null && !reportedDestination.equals(authVpa, ignoreCase = true)) {
            reportedDestination
        } else {
            null
        }

        val request = CustomerKillSwitchRequest(
            loanId = loanId,
            customerId = customerId,
            intentId = intent?.payload?.intentId,
            token = intent?.token,
            reportedDestination = destToReport,
            reason = reason,
        )

        // Always remove this token and clear active intent immediately to stop loops
        intent?.token?.let { resolvedTokens.add(it) }
        activeIntent = null
        showIntentPopup = false

        val res = ApiClient.service.killSwitch(request)
        if (res.isSuccessful && res.body() != null) {
            val responseBody = res.body()!!
            lastKillSwitchResponse = responseBody
            if (responseBody.trustReceipt != null) {
                lastReceipt = responseBody.trustReceipt
            }
            onComplete?.invoke(true)
        } else {
            errorMessage = "Kill switch trigger error (${res.code()})"
            onComplete?.invoke(false)
        }
    }

    /**
     * Handles an incoming deep link token from Telegram, WhatsApp, or browser:
     * Decodes the cryptographic token payload locally for immediate instant rendering,
     * validates with backend, and navigates directly into the Action Gate.
     */
    fun handleDeepLinkToken(token: String, onLoaded: (() -> Unit)? = null) = launchSafely {
        deepLinkHandled = true
        showIntentPopup = false
        pendingNavigation = "action_gate"

        // Decode token payload locally for instant UI response without waiting
        try {
            val tokenParts = token.split(".")
            if (tokenParts.isNotEmpty()) {
                val decodedBytes = Base64.decode(tokenParts[0], Base64.URL_SAFE or Base64.NO_PADDING)
                val jsonStr = String(decodedBytes, Charsets.UTF_8)
                val adapter = moshi.adapter(IntentPayload::class.java)
                val parsedPayload = adapter.fromJson(jsonStr)
                if (parsedPayload != null) {
                    activeIntent = SignedIntent(
                        token = token,
                        payload = parsedPayload,
                        expiresInSeconds = 180,
                        status = "ACTIVE",
                        deepLink = "pramaan://verify?token=$token"
                    )
                }
            }
        } catch (e: Exception) {
            Log.w("PramaanViewModel", "Direct token decoding fallback to server sync", e)
        }

        // Synchronize with server
        checkForIncomingInteraction {
            pendingNavigation = "action_gate"
            onLoaded?.invoke()
        }
    }

    fun loadReceiptHistory() = launchSafely {
        val customerId = account?.customerId ?: DEMO_CUSTOMER_ID
        val res = ApiClient.service.getCustomerReceipts(customerId)
        if (res.isSuccessful && res.body() != null) {
            receiptsHistory = res.body()!!
        }
    }

    fun verifyPublicReceipt(receiptId: String) = launchSafely {
        val res = ApiClient.service.verifyPublicReceipt(receiptId)
        if (res.isSuccessful) {
            publicVerificationResult = res.body()
        } else {
            errorMessage = "Public verification failed (${res.code()})"
        }
    }

    fun submitKycImage(file: File) = launchSafely {
        val body = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
        val part = MultipartBody.Part.createFormData("file", file.name, body)
        val res = ApiClient.service.kycAuthenticity(part)
        if (res.isSuccessful) {
            authenticityResult = res.body()
        } else {
            errorMessage = "KYC authenticity evaluation failed (${res.code()})"
        }
    }

    fun resetDemoState(onComplete: (() -> Unit)? = null) = launchSafely {
        resolvedTokens.clear()
        activeIntent = null
        showIntentPopup = false
        deepLinkHandled = false
        lastVerifyResponse = null
        lastKillSwitchResponse = null
        lastReceipt = null
        errorMessage = null
        try {
            val res = ApiClient.service.resetDemo()
            if (res.isSuccessful) {
                Log.d("PramaanViewModel", "Demo reset successful: ${res.body()?.message}")
            } else {
                Log.w("PramaanViewModel", "Reset endpoint failed with code ${res.code()}")
            }
        } catch (e: Exception) {
            Log.w("PramaanViewModel", "Backend reset warning", e)
        }
        loadCustomerAccount()
        loadReceiptHistory()
        onComplete?.invoke()
    }

    private fun launchSafely(block: suspend () -> Unit) {
        viewModelScope.launch {
            isLoading = true
            try {
                block()
            } catch (e: Exception) {
                Log.e("PramaanViewModel", "Network error", e)
                errorMessage = e.localizedMessage ?: "Network connection error"
            } finally {
                isLoading = false
            }
        }
    }
}
