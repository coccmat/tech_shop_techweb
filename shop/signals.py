from django import dispatch


product_restocked = dispatch.Signal()
sale_confirmation= dispatch.Signal()
