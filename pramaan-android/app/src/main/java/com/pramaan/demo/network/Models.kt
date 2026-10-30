package com.pramaan.demo.network

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class Account(
    @Json(name = "loan_id") val loanId: String,
    @Json(name = "customer_id") val customerId: String,
    @Json(name = "customer_name") val customerName: String,
    @Json(name = "product_name") val productName: String = "TVS Two-Wheeler Loan",
    val purpose: String,
    val amount: Double,
    @Json(name = "due_date") val dueDate: String,
    @Json(name = "authorized_destination") val authorizedDestination: String,
)

@JsonClass(generateAdapter = true)
data class IntentPayload(
    @Json(name = "intent_id") val intentId: String = "",
    @Json(name = "customer_id") val customerId: String,
    @Json(name = "loan_id") val loanId: String,
    val purpose: String,
    val amount: Double,
    val action: String,
    val destination: String?,
    val channel: String,
    @Json(name = "partner_id") val partnerId: String = "PARTNER-TVS-01",
    @Json(name = "partner_name") val partnerName: String = "TVS Credit Direct",
    @Json(name = "agent_id") val agentId: String = "AGT-7701",
    @Json(name = "agent_name") val agentName: String = "Suresh Menon",
    @Json(name = "issued_at") val issuedAt: String,
    @Json(name = "expires_at") val expiresAt: String,
    val nonce: String,
    val audience: String = "tvs_customer_app",
    @Json(name = "session_id") val sessionId: String? = null,
    @Json(name = "claimed_destination") val claimedDestination: String? = null,
    @Json(name = "claimed_amount") val claimedAmount: Double? = null,
    @Json(name = "claimed_agent_id") val claimedAgentId: String? = null,
    @Json(name = "scenario_tag") val scenarioTag: String? = null,
    @Json(name = "scenario_title") val scenarioTitle: String? = null,
)

@JsonClass(generateAdapter = true)
data class SignedIntent(
    val token: String,
    val payload: IntentPayload,
    @Json(name = "expires_in_seconds") val expiresInSeconds: Int,
    val status: String = "ACTIVE",
    @Json(name = "deep_link") val deepLink: String? = null,
)

@JsonClass(generateAdapter = true)
data class CustomerKillSwitchRequest(
    @Json(name = "loan_id") val loanId: String,
    @Json(name = "customer_id") val customerId: String? = "CUST-001",
    @Json(name = "intent_id") val intentId: String? = null,
    val token: String? = null,
    @Json(name = "reported_destination") val reportedDestination: String? = null,
    val reason: String = "Customer marked: I DON'T TRUST THIS REQUEST",
)

@JsonClass(generateAdapter = true)
data class CustomerKillSwitchResponse(
    val success: Boolean,
    @Json(name = "incident_id") val incidentId: String,
    val status: String,
    val message: String,
    @Json(name = "quarantined_destination") val quarantinedDestination: String? = null,
    @Json(name = "revoked_intent_id") val revokedIntentId: String? = null,
    val timestamp: String? = null,
    @Json(name = "trust_receipt") val trustReceipt: TrustReceipt? = null,
)

@JsonClass(generateAdapter = true)
data class ClaimedRequest(
    @Json(name = "loan_id") val loanId: String,
    val purpose: String,
    val amount: Double,
    val action: String,
    val destination: String? = null,
    @Json(name = "agent_id") val agentId: String? = null,
    @Json(name = "device_confirmed") val deviceConfirmed: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class TrustReceipt(
    @Json(name = "receipt_id") val receiptId: String,
    @Json(name = "interaction_id") val interactionId: String,
    @Json(name = "customer_id") val customerId: String,
    @Json(name = "loan_id") val loanId: String,
    val purpose: String,
    val action: String,
    val amount: Double,
    val destination: String?,
    val channel: String,
    @Json(name = "partner_name") val partnerName: String,
    @Json(name = "agent_name") val agentName: String,
    @Json(name = "agent_id") val agentId: String,
    val decision: String,
    @Json(name = "decision_reason") val decisionReason: String,
    val timestamp: String,
    @Json(name = "authorization_ref") val authorizationRef: String,
    val signature: String,
    @Json(name = "key_id") val keyId: String? = null,
    @Json(name = "policy_version") val policyVersion: String? = null,
)

@JsonClass(generateAdapter = true)
data class VerifyRequest(
    val token: String,
    val claimed: ClaimedRequest,
    @Json(name = "correlation_id") val correlationId: String? = null,
    val idempotent: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class VerifyResponse(
    val matched: Boolean,
    val decision: String = "ALLOWED",
    val reason: String,
    @Json(name = "signature_valid") val signatureValid: Boolean,
    val fresh: Boolean,
    @Json(name = "agent_authorized") val agentAuthorized: Boolean = true,
    @Json(name = "destination_verified") val destinationVerified: Boolean = true,
    @Json(name = "assurance_level") val assuranceLevel: String = "STANDARD",
    @Json(name = "risk_signals") val riskSignals: List<String> = emptyList(),
    @Json(name = "policy_version") val policyVersion: String = "3.2.0",
    @Json(name = "reason_code") val reasonCode: String = "POL_AUTHORIZED",
    @Json(name = "correlation_id") val correlationId: String? = null,
    val idempotent: Boolean = false,
    @Json(name = "on_record") val onRecord: IntentPayload? = null,
    @Json(name = "trust_receipt") val trustReceipt: TrustReceipt? = null,
)

@JsonClass(generateAdapter = true)
data class AuthenticityResponse(
    @Json(name = "risk_score") val riskScore: Double,
    val verdict: String,
    val note: String,
    @Json(name = "model_version") val modelVersion: String = "DeepWatch-v2-Prototype",
)

@JsonClass(generateAdapter = true)
data class PublicReceiptVerification(
    val valid: Boolean,
    @Json(name = "receipt_id") val receiptId: String,
    @Json(name = "interaction_id") val interactionId: String? = null,
    val decision: String,
    val action: String,
    val amount: Double,
    @Json(name = "masked_customer") val maskedCustomer: String,
    val timestamp: String,
    @Json(name = "authorization_ref") val authorizationRef: String,
    val authority: String = "TVS Credit Services Ltd.",
    @Json(name = "key_id") val keyId: String? = null,
    @Json(name = "policy_version") val policyVersion: String? = null,
    val status: String,
)

@JsonClass(generateAdapter = true)
data class ResetResponse(
    val status: String = "RESET_SUCCESS",
    val message: String = "PRAMAAN demo state reset to pristine baseline.",
    val timestamp: String = "",
)
