package com.ng.controller;

import com.razorpay.RazorpayException;
import com.stripe.exception.StripeException;
import com.ng.domain.PaymentMethod;
import com.ng.exception.UserException;
import com.ng.modal.PaymentOrder;
import com.ng.modal.User;
import com.ng.payload.response.PaymentLinkResponse;
import com.ng.service.PaymentService;
import com.ng.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/payments")
@RequiredArgsConstructor
public class PaymentController {

    private final PaymentService paymentService;
    private final UserService userService;


    @PostMapping("/create")
    public ResponseEntity<PaymentLinkResponse> createPaymentLink(
            @RequestHeader("Authorization") String jwt,
            @RequestParam Long planId,
            @RequestParam PaymentMethod paymentMethod) throws UserException, RazorpayException, StripeException {


            User user = userService.getUserFromJwtToken(jwt);



            PaymentLinkResponse paymentLinkResponse =
                    paymentService.createOrder(user, planId, paymentMethod);
            return ResponseEntity.ok(paymentLinkResponse);


    }



    @PatchMapping("/proceed")
    public ResponseEntity<Boolean> proceedPayment(
            @RequestParam String paymentId,
            @RequestParam String paymentLinkId) throws Exception {

            PaymentOrder paymentOrder = paymentService.
                    getPaymentOrderByPaymentId(paymentLinkId);
            Boolean success = paymentService.ProceedPaymentOrder(
                    paymentOrder,
                    paymentId, paymentLinkId);
            return ResponseEntity.ok(success);

    }


}
