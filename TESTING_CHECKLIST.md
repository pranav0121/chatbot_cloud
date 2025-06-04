# Manual Testing Checklist for Chatbot Fixes

## Pre-Testing Setup
- [ ] Start the chatbot application: `python app.py`
- [ ] Open browser to `http://localhost:5000`
- [ ] Open browser developer console (F12) to monitor for errors

## Fix 1: Category Input Section Display

### Test Steps:
1. [ ] Open the chatbot interface
2. [ ] Click "Need Help? Click to chat with us!" button
3. [ ] Select any category (Payments, Product Issues, Technical Glitches, General Inquiries)
4. [ ] Verify the following appears after category selection:
   - [ ] Common issues list displays
   - [ ] "Type your [category] question here..." input box appears below
   - [ ] Input placeholder text matches selected category
   - [ ] No JavaScript errors in console

### Expected Behavior:
- Category input section should appear immediately after category selection
- Should work even if common issues fail to load
- Input should be focused and ready for typing

### Test Different Scenarios:
- [ ] Test with good internet connection
- [ ] Test with simulated network failure (disconnect internet briefly)
- [ ] Test rapid category switching
- [ ] Test on mobile device (responsive)

---

## Fix 2: Paste Functionality for Image Uploads

### Test Steps:
1. [ ] Copy an image to clipboard (screenshot, image file, etc.)
2. [ ] Test pasting in each of these locations:
   - [ ] Main chat message input
   - [ ] Category question input box
   - [ ] Issue description textarea (if visible)
   - [ ] Live chat message input

### Expected Behavior:
- [ ] Image should be detected from clipboard
- [ ] Preview should appear immediately
- [ ] Success notification should display
- [ ] File should be prepared for upload
- [ ] Console should show paste event logs

### Test Different Image Sources:
- [ ] Screenshot from Snipping Tool
- [ ] Copy image from web browser
- [ ] Copy image from file explorer
- [ ] Copy image from image editing software

### Test File Validation:
- [ ] Paste very large image (should show size limit error)
- [ ] Paste non-image content (should allow normal text paste)

---

## Fix 3: Admin Panel Image Viewing

### Test Steps:
1. [ ] Create a ticket with image attachment using the main interface
2. [ ] Note the ticket ID from the success message
3. [ ] Navigate to admin panel: `http://localhost:5000/admin`
4. [ ] Go to "Tickets" section
5. [ ] Find the ticket with attachment
6. [ ] Click the "View" button (eye icon)

### Expected Behavior:
- [ ] Ticket details modal opens
- [ ] Attachments section is visible below message content
- [ ] Image thumbnail displays correctly
- [ ] Clicking thumbnail opens full-size modal
- [ ] Image loads in full-size modal
- [ ] Download button works in modal
- [ ] File size and name are displayed correctly

### Test Different Scenarios:
- [ ] Ticket with multiple images
- [ ] Ticket with no attachments (should not show attachment section)
- [ ] Large image files
- [ ] Different image formats (PNG, JPG, GIF)

---

## Cross-Browser Testing

### Test in Multiple Browsers:
- [ ] Chrome
- [ ] Firefox  
- [ ] Safari (if on Mac)
- [ ] Edge

### Mobile Testing:
- [ ] Test on mobile browser
- [ ] Test paste functionality on mobile
- [ ] Test admin panel responsiveness

---

## Performance Testing

### Load Testing:
- [ ] Create multiple tickets rapidly
- [ ] Upload multiple large images
- [ ] Test admin panel with many tickets
- [ ] Monitor browser memory usage

### Network Testing:
- [ ] Test with slow internet connection
- [ ] Test with intermittent connectivity
- [ ] Test offline behavior (should gracefully handle errors)

---

## Error Handling Testing

### Intentional Error Scenarios:
- [ ] Try to paste extremely large files
- [ ] Disconnect network during upload
- [ ] Try to access admin panel during server restart
- [ ] Submit empty forms
- [ ] Paste unsupported file types

### Expected Error Behavior:
- [ ] User-friendly error messages display
- [ ] No JavaScript crashes or white screens
- [ ] System recovers gracefully
- [ ] Console errors are informative

---

## Integration Testing

### End-to-End Workflow:
1. [ ] User selects category
2. [ ] Input section appears
3. [ ] User pastes image
4. [ ] User types message
5. [ ] User submits ticket
6. [ ] Ticket created successfully
7. [ ] Admin views ticket
8. [ ] Admin sees image attachment
9. [ ] Admin can view full-size image

### Multiple User Simulation:
- [ ] Test with multiple browser windows
- [ ] Simulate concurrent users
- [ ] Test database consistency

---

## Final Verification

### Success Criteria:
- [ ] All three fixes work independently
- [ ] All three fixes work together
- [ ] No JavaScript errors in console
- [ ] No network request failures
- [ ] User experience is smooth and intuitive
- [ ] Admin panel functions correctly
- [ ] File uploads work end-to-end

### Documentation:
- [ ] All fixes documented in FIXES_SUMMARY.md
- [ ] Code comments are clear and helpful
- [ ] No debugging console.log statements in production code

---

## Sign-off

**Tester Name:** _________________
**Date:** _________________
**Environment:** _________________

**Overall Result:** 
- [ ] ✅ All tests passed - Ready for production
- [ ] ⚠️  Some issues found - Needs fixes
- [ ] ❌ Major issues found - Not ready

**Additional Notes:**
_________________________________________________
_________________________________________________
_________________________________________________
