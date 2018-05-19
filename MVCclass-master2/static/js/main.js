/*
 * This is the Javascript file that makes requests to our controller.
 * We have prepared one API that makes requests in two unique ways
 * The filter option requests for data to be displayed and the download option
 * requests for data to be in a downloadable form
 */

$('#filter-btn').click(function() {
window.location.href="/index?name="
+ $("#presidents").val() + "&year="
+ $("#year").val() + "&month="
+ $("#month") + "&document_type="
+ $("documenttype").val() + "&topic="
+ $("#topic").val() + "&people="
});
