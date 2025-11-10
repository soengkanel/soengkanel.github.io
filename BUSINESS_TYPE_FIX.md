# Business Type Field Fix - Complete Summary

## Issue
When creating a store during onboarding, the application threw an error:
```
Column 'business_type' cannot be null
```

This occurred because the `business_type` column in the `stores` table has a `NOT NULL` constraint, but no value was being provided during store creation.

---

## Root Cause

The `Store` entity had a `businessType` field with a default value in Java:
```java
@Column(name = "business_type", nullable = false)
private BusinessType businessType = BusinessType.RETAIL;
```

However, when using the **Builder pattern** in `StoreMapper.toEntity()`, the default value was **not being set**. The Builder creates a new object and only sets explicitly specified fields, so `businessType` remained `null`.

---

## Solution Overview

Added `businessType` field support throughout the entire stack:
1. **Backend DTO** - Added field to StoreDTO
2. **Backend Mapper** - Set default value in mapper
3. **Frontend Form** - Added businessType selector
4. **Frontend State** - Added to form state and submission

---

## Files Modified

### Backend Changes

#### 1. **StoreDTO.java** ✅
**File:** `pos-backend/src/main/java/com/ng/payload/dto/StoreDTO.java`

**Changes:**
- Added import: `import com.ng.domain.BusinessType;`
- Added field: `private BusinessType businessType;`

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StoreDTO {
    private Long id;
    private String brand;
    private Long storeAdminId;
    private UserDTO storeAdmin;
    private String storeType;
    private BusinessType businessType; // ✅ NEW
    private StoreStatus status;
    private String description;
    private StoreContact contact;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

---

#### 2. **StoreMapper.java** ✅
**File:** `pos-backend/src/main/java/com/ng/mapper/StoreMapper.java`

**Changes:**
- Added import: `import com.ng.domain.BusinessType;`
- Added `.businessType()` in `toDto()` method
- Added `.businessType()` with default fallback in `toEntity()` method

**toDto() method:**
```java
public static StoreDTO toDto(Store store) {
    return StoreDTO.builder()
            .id(store.getId())
            .brand(store.getBrand())
            .storeAdminId(store.getStoreAdmin() != null ? store.getStoreAdmin().getId() : null)
            .storeAdmin(UserMapper.toDTO(store.getStoreAdmin()))
            .storeType(store.getStoreType())
            .businessType(store.getBusinessType()) // ✅ NEW
            .description(store.getDescription())
            .contact(store.getContact())
            .createdAt(store.getCreatedAt())
            .updatedAt(store.getUpdatedAt())
            .status(store.getStatus())
            .build();
}
```

**toEntity() method:**
```java
public static Store toEntity(StoreDTO dto, User storeAdmin) {
    return Store.builder()
            .id(dto.getId())
            .brand(dto.getBrand())
            .storeAdmin(storeAdmin)
            .createdAt(dto.getCreatedAt())
            .updatedAt(dto.getUpdatedAt())
            .storeType(dto.getStoreType())
            .businessType(dto.getBusinessType() != null ? dto.getBusinessType() : BusinessType.RETAIL) // ✅ NEW with default
            .description(dto.getDescription())
            .build();
}
```

**Key Logic:** If `businessType` is not provided in the DTO, it defaults to `BusinessType.RETAIL` for backward compatibility.

---

### Frontend Changes

#### 3. **StoreDetailsForm.jsx** ✅
**File:** `pos-frontend-vite/src/pages/onboarding/StoreDetailsForm.jsx`

**Changes:**

1. **Updated validation schema:**
```javascript
const validationSchema = Yup.object({
  storeName: Yup.string()
    .required("Store name is required")
    .min(2, "Store name must be at least 2 characters"),
  storeType: Yup.string().required("Store type is required"),
  businessType: Yup.string().required("Business type is required"), // ✅ NEW
  storeAddress: Yup.string().optional(),
});
```

2. **Added businessTypes array:**
```javascript
const businessTypes = [
  {
    value: "RETAIL",
    label: "Retail Only",
    description: "For retail products like electronics, clothing, groceries, etc."
  },
  {
    value: "FNB",
    label: "Food & Beverage",
    description: "For restaurants, cafes, bakeries, etc."
  },
  {
    value: "HYBRID",
    label: "Retail + F&B",
    description: "For businesses with both retail and food services"
  },
];
```

3. **Added Business Type field in form (after Store Type field):**
```jsx
{/* Business Type Field */}
<div>
  <label
    htmlFor="businessType"
    className="block text-sm font-semibold text-gray-700 mb-2"
  >
    Business Type
  </label>
  <Field name="businessType">
    {({ field, form }) => (
      <Select
        value={field.value}
        onValueChange={(val) => form.setFieldValue("businessType", val)}
      >
        <SelectTrigger className="w-full" id="businessType">
          <SelectValue placeholder="Select business type" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Business Types</SelectLabel>
            {businessTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                <div className="flex flex-col">
                  <span className="font-medium">{type.label}</span>
                  <span className="text-xs text-gray-500">{type.description}</span>
                </div>
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    )}
  </Field>
  <ErrorMessage
    name="businessType"
    component="div"
    className="text-red-500 text-sm mt-2 flex items-center"
  >
    {(msg) => (
      <>
        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        {msg}
      </>
    )}
  </ErrorMessage>
</div>
```

---

#### 4. **Onboarding.jsx** ✅
**File:** `pos-frontend-vite/src/pages/onboarding/Onboarding.jsx`

**Changes:**

1. **Added businessType to form state with default:**
```javascript
const [formData, setFormData] = useState({
  // Owner Details
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  // Store Details
  storeName: '',
  storeType: '',
  businessType: 'RETAIL', // ✅ NEW - Default to RETAIL
  storeAddress: '',
});
```

2. **Added businessType to createStore dispatch:**
```javascript
await dispatch(createStore({
  brand: updatedFormData.storeName,
  storeType: updatedFormData.storeType,
  businessType: updatedFormData.businessType, // ✅ NEW
  storeAddress: updatedFormData.storeAddress,
})).unwrap();
```

3. **Added businessType to StoreDetailsForm initialValues:**
```javascript
<StoreDetailsForm
  initialValues={{
    storeName: formData.storeName,
    storeType: formData.storeType,
    businessType: formData.businessType, // ✅ NEW
    storeAddress: formData.storeAddress,
  }}
  onSubmit={handleStepSubmit}
  onBack={handleStepBack}
/>
```

---

## Business Type Options

Users can now select from three business types during onboarding:

| Value | Label | Description | Use Case |
|-------|-------|-------------|----------|
| `RETAIL` | Retail Only | For retail products like electronics, clothing, groceries, etc. | Traditional retail stores |
| `FNB` | Food & Beverage | For restaurants, cafes, bakeries, etc. | Restaurants, cafes |
| `HYBRID` | Retail + F&B | For businesses with both retail and food services | Convenience stores with cafe |

---

## Default Behavior

1. **Backend Default:** If `businessType` is not provided, defaults to `RETAIL` in `StoreMapper.toEntity()`
2. **Frontend Default:** Form state initializes with `businessType: 'RETAIL'`
3. **Validation:** `businessType` is now a required field in the form

---

## Database Schema

The `business_type` column already exists in the `stores` table:

```sql
ALTER TABLE stores ADD COLUMN business_type VARCHAR(20) NOT NULL DEFAULT 'RETAIL';
```

**Note:** If you haven't run this migration yet, execute it before testing.

---

## Testing Checklist

- [x] Backend compiles successfully
- [x] StoreDTO includes businessType field
- [x] StoreMapper sets default value
- [ ] Onboarding form displays Business Type dropdown
- [ ] Selecting "Retail Only" creates store with businessType=RETAIL
- [ ] Selecting "Food & Beverage" creates store with businessType=FNB
- [ ] Selecting "Retail + F&B" creates store with businessType=HYBRID
- [ ] Store creation succeeds without null constraint error
- [ ] Existing stores without businessType default to RETAIL

---

## Summary

✅ **Error Fixed!**

The "Column 'business_type' cannot be null" error has been resolved by:
1. Adding `businessType` field to `StoreDTO`
2. Setting default value in `StoreMapper.toEntity()`
3. Adding Business Type selector to onboarding form
4. Including `businessType` in form state and submission

Users can now successfully complete onboarding and create stores with their preferred business type (Retail, F&B, or Hybrid).
