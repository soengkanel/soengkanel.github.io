import { useState } from "react";
import { Card, CardContent } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Minus, Plus, Trash2, Percent, DollarSign } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../../../components/ui/popover";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { RadioGroup, RadioGroupItem } from "../../../components/ui/radio-group";

const CartItem = ({ item, updateCartItemQuantity, removeFromCart, setItemDiscount }) => {
  const [discountType, setDiscountType] = useState(item.discount?.type || "none");
  const [discountValue, setDiscountValue] = useState(item.discount?.value || 0);

  const calculateItemDiscount = () => {
    const itemSubtotal = item.sellingPrice * item.quantity;
    if (!item.discount || item.discount.type === "none") return 0;

    if (item.discount.type === "percentage") {
      return itemSubtotal * (item.discount.value / 100);
    } else if (item.discount.type === "fixed") {
      return item.discount.value * item.quantity;
    }
    return 0;
  };

  const applyDiscount = () => {
    if (setItemDiscount) {
      setItemDiscount({
        id: item.id,
        discount: { type: discountType, value: parseFloat(discountValue) || 0 }
      });
    }
  };

  const itemSubtotal = item.sellingPrice * item.quantity;
  const itemDiscountAmount = calculateItemDiscount();
  const itemTotal = itemSubtotal - itemDiscountAmount;

  return (
    <Card key={item.id} className="border-l-4 border-l-green-700">
      <CardContent className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="font-medium">{item.name}</h3>
            <p className="text-sm text-muted-foreground">{item.sku}</p>
            {item.discount && item.discount.type !== "none" && (
              <Badge variant="secondary" className="mt-1 text-xs">
                {item.discount.type === "percentage"
                  ? `${item.discount.value}% off`
                  : `៛${item.discount.value} off`}
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center border rounded">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => updateCartItemQuantity(item.id, item.quantity - 1)}
              >
                <Minus className="w-4 h-4" />
              </Button>
              <span className="px-3 py-1 text-sm font-medium min-w-[3rem] text-center">
                {item.quantity}
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => updateCartItemQuantity(item.id, item.quantity + 1)}
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>

            {/* Discount Button */}
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 w-8 p-0"
                >
                  <Percent className="w-4 h-4" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-80">
                <div className="space-y-4">
                  <h4 className="font-medium">Item Discount</h4>
                  <RadioGroup value={discountType} onValueChange={setDiscountType}>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="none" id={`none-${item.id}`} />
                      <Label htmlFor={`none-${item.id}`}>No Discount</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="percentage" id={`percentage-${item.id}`} />
                      <Label htmlFor={`percentage-${item.id}`}>Percentage</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="fixed" id={`fixed-${item.id}`} />
                      <Label htmlFor={`fixed-${item.id}`}>Fixed Amount</Label>
                    </div>
                  </RadioGroup>

                  {discountType !== "none" && (
                    <div className="space-y-2">
                      <Label>
                        {discountType === "percentage" ? "Discount (%)" : "Discount Amount (៛)"}
                      </Label>
                      <Input
                        type="number"
                        value={discountValue}
                        onChange={(e) => setDiscountValue(e.target.value)}
                        placeholder="0"
                      />
                    </div>
                  )}

                  <Button onClick={applyDiscount} className="w-full">
                    Apply Discount
                  </Button>
                </div>
              </PopoverContent>
            </Popover>

            <div className="text-right">
              <p className="font-medium">៛{item.sellingPrice}</p>
              {itemDiscountAmount > 0 && (
                <p className="text-xs text-red-500 line-through">
                  ៛{itemSubtotal.toFixed(2)}
                </p>
              )}
              <p className="text-sm font-bold text-green-600">
                ៛{itemTotal.toFixed(2)}
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
              onClick={() => removeFromCart(item.id)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CartItem;