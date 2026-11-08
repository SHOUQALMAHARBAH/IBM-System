# The decision index — فهرسُ قراراتِ المالكة

**٤٩ قراراً. كلُّ رقمٍ مذكورٍ في الكودِ له سطرٌ هنا وملفٌّ في `docs/`.**

**49 decisions. Every decision number cited anywhere in the code has a row here and a file in `docs/`.**

> **ليش هذا الملفُّ موجود.** في الكودِ مكتوبٌ «قرارُ المالكةِ ٤٨» في ٧٤ موضعاً — **ومن غيرِ هذا الفهرسِ ما في طريقةٌ تعرف شو هو القرارُ ٤٨ إلّا أن تسألَها.** وقاعدتُها: *«ما بدي حد يرجعلي»*. **فهذا الفهرسُ هو البديلُ عن سؤالِها.**
>
> **Why this file exists.** `OWNER DECISION 48` is cited 74 times in the code. Without this index the only way to learn what it says is to ask her — and her standing instruction is that nobody should have to. **This index is the answer to that question, so she does not have to be.**
>
> **التقسيمُ بقرارِها:** **النصوصُ في `docs/`** حيث العُرفُ قائمٌ بثمانيةِ ملفّاتٍ سابقة · **والفهرسُ هنا** لأنّ الدماغَ أوّلُ ما يُقرأ. ⟶ **بيتٌ واحدٌ لكلِّ حقيقة: الفهرسُ يربط، ولا يُعيد كتابةَ ما في الملفّات.**
>
> **كيف يبقى حيّاً.** قوانينُ `workspace-updates` و`definition-of-done` و`brain-freshness` تسأل عند كلِّ تغيير: **«شو صار كاذباً في الوثائق؟»** — **وهذا الفهرسُ داخلٌ في ذاك السؤال.** فقرارٌ جديدٌ يُذكَر في الكودِ بلا سطرٍ هنا **هو عطلٌ لا تأخير.**
>
> **وطريقةُ عدِّ الـ٤٧، عشان تُعاد لا تُؤخَذ:** بحثٌ في `apps/` و`packages/` عن `decision` متبوعةً برقم، ثمّ الأرقامُ المختلفة. **يطلع ٤٨ — والرقمُ ٢٠٢ منها ليس قراراً، هو التاريخُ `2026-10-29` قرأه المُطابِقُ غلطاً.** ⟶ **٤٧.**
>
> **Re-derived independently, 2026-11-08, and the two routes agree on 47 by different arithmetic.** Running that method over tracked files under `apps/` + `packages/` on `main` gives **52** distinct numbers, not 48. Five are the matcher, not decisions: `409` is an HTTP status in `(409)` after the word `ClientDecision`, `6` is `Decision (6 outcomes)`, `17` is the backlog's `Client Decision #17`, `1` is the fixture id `'act-decision-1'`, and **`98` is real but already had its file before this batch** (`docs/decision-98-widened-and-concentration.md`). 52 - 4 phantoms - 1 already-filed = **47**, and the 47 numbers match the 47 filenames exactly, in both directions. The date `2026-10-29` is excluded as a date rather than read as `202`. `npm run check:decision-index` is the gate; it declares this pattern and both exclusion lists in the script, so the figure is re-run and never recalled.
>
> **CORRECTED 2026-11-08, SAME DAY, AND THE CORRECTION IS WORTH MORE THAN THE NUMBER: THE TOTAL IS 48, AND THE TWO ROUTES AGREED ON 47 BECAUSE THEY SHARED ONE BLIND SPOT.** The 48th is **decision 33**, and it is cited in **ten places** — nine of which a literal search finds, the tenth wrapping a line inside a block comment, which is why its own file states nine and is right to. Both counts missed it for the same structural reason: it appears ONLY inside the phrase `decisions 32 and 33`, never once on its own, so every matcher anchored on the word `decision` immediately before a number read the `32` and was blind to the `33`. **Two independent counts agreeing is evidence only when they are independent in the thing that can be wrong** — and here they shared their matcher's shape, so the agreement at 47 confirmed the arithmetic and could not confirm the coverage. The Arabic paragraph above is left exactly as written: it is a true account of a method that really does yield 47, and the 47 is the history rather than an error to erase. **The gate now walks a multi-number citation**, self-tested in the two-number and the four-number shape, so this hole cannot quietly reopen — and its own count of decision 33 is **wrap-tolerant**, because the tenth citation breaks across a line inside a block comment and a single-line search finds only nine.

> **🔴 وأُضيفَ القرارُ ٩٨ في ٨ تشرين الثاني، والعددُ صار ٤٩ لا ٤٨ — والسببُ يستاهل يُقرأ.** **ملفُّه كان موجوداً في `docs/` من قبلِ هذي الدفعة، فاستُثنيَ من عدِّ الدفعةِ بحقٍّ** (الفقرةُ فوق تقول ذلك بنصِّها) — **لكنّه استُثنيَ من الفهرسِ كذلك، فبقي رقمٌ مذكورٌ في الكودِ بلا سطرٍ هنا، والرأسُ يقول إنّ كلَّ رقمٍ له سطر.** ⟶ **يعني الفهرسُ ادّعى اكتمالاً ما كان مكتملاً، وهذا بالزبط العطلُ اللي هذا الفهرسُ موجودٌ ليمنعَه.**
>
> **ومقيسٌ من المستودع:** `ls docs/decision-*.md | grep -cE 'decision-[0-9]+-'` **يطلّع ٤٩**، وصفوفُ هذا الجدولِ كانت **٤٨**، والناقصُ واحدٌ هو **٩٨**. **و`ls docs/decision*.md | wc -l` يطلّع ٥٦ — والفرقُ سبعةُ ملفّاتٍ مسمّاةٍ بأسمائِها لا بأرقامِها، وهي ليست نقصاً في الفهرس.** ⟶ **فالرقمُ ٤٩ أو ٥٦ أو ٤٨ صحيحٌ كلُّه، كلٌّ بوحدةِ عدِّه — ومن يقرأ رقماً بلا وحدتِه يفهم غيرَ اللي صار.**
>
> **🔴 وملاحظةٌ للمهندس:** **البوّابةُ عدَّت وطبعَت «٤٩ مذكوراً · ٤٩ ملفاً · ٤٨ سطراً» وخرجَت بصفر.** **فهي تقرّر الفرقَ ولا توقفه.** ⟶ **وبوّابةٌ تطبع الثقبَ ولا تمنعه تُقرأ خضراءَ وتُعبَر.**


## الفهرس

| # | القرار بجملة | الملفّ | قُرِّر ولم يُبنَ |
|---|---|---|---|
| **٢** | الجمل اللي تشرح نتيجة فحص العميل صارت تُحفَظ في قاموس كلمات النظام، والخادم يرسل رمزاً فقط. فالكلمة ملكنا، لا ملك الخادم. | [`decision-2-explaining-sentence-moved-into.md`](../../docs/decision-2-explaining-sentence-moved-into.md) |  |
| **٣** | في عمليات حسّاسة ما بيصير شخص واحد يكمّلها لحاله: واحد يعمل، وواحد ثاني يصدّق. وكل زوج من هذول مكتوب في ملف واحد. | [`decision-3-performs-operation-approves.md`](../../docs/decision-3-performs-operation-approves.md) |  |
| **٩** | ما بنبني عموداً نحن أصلاً ما عندنا البيانات اللي تنزل فيه. فربط فروع الترخيص بأنواع التأمين عندنا مؤجَّل لحين وصول القائمة الرسمية. | [`decision-9-mapping-column-built-until.md`](../../docs/decision-9-mapping-column-built-until.md) | 🔴 **نعم** |
| **١١** | لمّا نسجّل في سجل التفتيش إنه أُنشئ مدير لشركة تأمين، نكتب كم صلاحية أُعطيت — لا أسماء الصلاحيات. | [`decision-11-audit-row-records-count.md`](../../docs/decision-11-audit-row-records-count.md) |  |
| **١٢** | شاشة طلبات عروض الأسعار إلها مدخل في القائمة الجانبية، والمدخل يظهر بالزبط لمن يحمل صلاحية قراءة الطلبات — لا أكثر ولا أقل. | [`decision-12-menu-entry-appears-exactly.md`](../../docs/decision-12-menu-entry-appears-exactly.md) |  |
| **١٣** | إذا كان الاختبار بيتأكد إن شيء ما ظاهر على الشاشة، لازم يحدد الجزء اللي دور فيه. ما بيصير يدور في الصفحة كلها. | [`decision-13-absence-test-looked.md`](../../docs/decision-13-absence-test-looked.md) |  |
| **١٨** | مسار إنشاء حساب مدير مكتب ما فيه خانة تحدد المكتب أبداً. الحساب يُنشأ في مكتب من طلب الإنشاء — فما في طريقة تمدّ ليد لمكتب ثاني. | [`decision-18-there-no-office-field.md`](../../docs/decision-18-there-no-office-field.md) |  |
| **٢٠** | رأسُ المالِ المطلوبُ للمكتبِ يُحسَب على عددِ الفروع. ونحن ما متأكدين من وحدةِ العدِّ. فالرقمُ يُحسَب ويُعرَض كما هو — ومعه على الشاشةِ أنّ وحدةَ العدِّ قيدَ التحقّق. | [`decision-20-deferred-reopening-condition-written.md`](../../docs/decision-20-deferred-reopening-condition-written.md) | 🔴 **نعم** |
| **٢١** | اسم أي خانة على الشاشة لازم يقول للموظف الخانة دي لشو. ما بيصير نأخذ عنوان عمود من جدول ونحطّه اسماً لخانة. | [`decision-21-label-field-name-column.md`](../../docs/decision-21-label-field-name-column.md) |  |
| **٢٢** | في كل زوج «من يعمل / من يصدّق»، الصلاحية المكتوبة في خانة «من يعمل» لازم تكون صلاحية بتحرس مساراً حقيقياً في النظام. وجودها في الكتالوج ما يكفي. | [`decision-22-recorded-permission-actually-gate.md`](../../docs/decision-22-recorded-permission-actually-gate.md) |  |
| **٢٥** | لما يُسجَّل مكتب جديد، تُرسَل دعوة لمديره. والرابط في الدعوة يستعمل نفس رمز إعادة تعيين كلمة المرور الموجود في النظام — لا رمزاً ثانياً اخترعناه للدعوات. | [`decision-25-invitation-reuses-password-reset.md`](../../docs/decision-25-invitation-reuses-password-reset.md) |  |
| **٢٦** | قبل إرسال دعوة لمدير شركة تأمين، النظام يسأل: هل هذه الشركة حيّة على المنصة؟ ويسأل عبر نفس الدالة اللي تجاوب هذا السؤال للمكاتب — لا عبر نسخة ثانية. | [`decision-26-organization-live-answered-function.md`](../../docs/decision-26-organization-live-answered-function.md) |  |
| **٢٨** | في حالات مسموحة بس فيها خطر. النظام ما يمنعها — يطلب من اللي بيعملها إقراراً في نفس الطلب إنه يعرف شو بيعمل. | [`decision-28-declares-does-refuse.md`](../../docs/decision-28-declares-does-refuse.md) |  |
| **٢٩** | لمّا تنتهي العلاقة مع العميل وتبدأ مدة الاحتفاظ القانونية، السجل ينتقل لحالة «الحجب»: ما حد يستعمله في الشغل، وما حد يقدر يتلفه، لحين تخلص المدة. | [`decision-29-after-relationship-ends-record.md`](../../docs/decision-29-after-relationship-ends-record.md) |  |
| **٣٢** | إذا صنف من السجلات إله حدّ أدنى في القانون، وما حطّينا له مدة احتفاظ بعد — الشاشة تعرض رقم المادة والحدّ الأدنى اللي يفرضه، لا خانة فاضية ولا رسالة خطأ. | [`decision-32-category-legal-floor-no.md`](../../docs/decision-32-category-legal-floor-no.md) |  |
| **٣٣** | جدول الاحتفاظ ينزل للمكتب وفيه ٨ فئات. الفئة اللي القانون فارض لها حدّاً أدنى تنزل بلا مدة أبداً. والفئة اللي ما في عليها حدّ قانونيّ تنزل ومعها مدة جاهزة. | [`decision-33-number-supplied-where-claims-nothing.md`](../../docs/decision-33-number-supplied-where-claims-nothing.md) |  |
| **٣٦** | في سجل في النظام لتضارب المصالح. وكل شخص يكتب فيه إقراره بنفسه — مش حد ثالث يكتب عنه. | [`decision-36-conflict-interest-register-recorded.md`](../../docs/decision-36-conflict-interest-register-recorded.md) |  |
| **٤١** | القائمة اللي يختار منها الموظف مستنداً، مفتوحة لمن يملك «قراءة المستندات» فقط. ومن يملك «قراءة تاريخ المستند» — زي المدقق الخارجي — ما بتفتح له. | [`decision-41-chooser-directory-id-lookup.md`](../../docs/decision-41-chooser-directory-id-lookup.md) |  |
| **٤٢** | الكلمة الواحدة ما بيصير تحمل معنيين في النظام. فـ«مهلة» عندنا تعني موعداً نهائياً لازم يُلحَق، و«مدّة» تعني طولاً زمنياً — واللي كان مخلوطاً صار مرتّباً. | [`decision-42-word-meaning-deadline-duration.md`](../../docs/decision-42-word-meaning-deadline-duration.md) |  |
| **٤٣** | شركة تأمين أُدخل لها تقييم مالي بالخطأ، لازم يكون في طريقة تمحيه. فصار في زر واحد يمحو التقييم وتاريخه معاً — ولا يظهر إلا إذا كان في تقييم فعلاً. | [`decision-43-clear-control-shown-only.md`](../../docs/decision-43-clear-control-shown-only.md) |  |
| **٤٤** | لما يُسجَّل إن حداً مدّ مدة احتفاظ سجل، السجل يحمل اسم الشخص — مش رقمه الداخلي. | [`decision-44-record-names-person-uuid.md`](../../docs/decision-44-record-names-person-uuid.md) |  |
| **٤٥** | إذا القائمة بيانات بتكبر وتنقص — كل عنصر يحمل اسمه العربي والإنجليزي معه في جواب الخادم. وإذا القائمة ثابتة وكلماتها أصلاً في قاموسنا — الخادم يرسل الرمز والشاشة تقرأ الكلمة من القاموس. | [`decision-45-owns-word-data-carries.md`](../../docs/decision-45-owns-word-data-carries.md) |  |
| **٤٦** | في ستّ عائلات سجلات لازم تُعرَض برقم يقرأه الإنسان، وما عندنا رقم إلها. والسبب إن إعطاءها رقماً يعني اختراع أول نظام ترقيم في هذا المنتج — وهذا شغل موديول ٧ المؤجَّل، لا شغل اليوم. | [`decision-46-six-records-have-no.md`](../../docs/decision-46-six-records-have-no.md) | 🔴 **نعم** |
| **٤٧** | إعدادات أمان المكتب سبعة، وكل واحد منهم يُعرَض ومعه الوحدة اللي يُقاس بها. ورقم بلا وحدة ما يُعرَض. | [`decision-47-seven-security-settings-each.md`](../../docs/decision-47-seven-security-settings-each.md) |  |
| **٤٨** | لما السجل يقول «فلان عمل هذا الإجراء»، الاسم يجي من ملف الموظف. وإذا الحساب ما له ملف موظف، يجي من الحساب نفسه. ومن مكان واحد في النظام، لا كل شاشة تجيبه بطريقتها. | [`decision-48-place-answers-did.md`](../../docs/decision-48-place-answers-did.md) |  |
| **٤٩** | لما يُعرَض سجل على شاشة: إذا كانت أنواع السجلات محصورة ومعروفة، يُعرَض اسمه العربي. وإذا كانت مفتوحة أو تكبر، يُعرَض نوعه ورقمه. | [`decision-49-name-set-closed-type.md`](../../docs/decision-49-name-set-closed-type.md) |  |
| **٥٠** | إذا بوليصة أُلغيت قبل ما يُصدَر لها رقم، الشاشة تعرضها باسم العميل ونوع التأمين — لا بمعرّف قاعدة البيانات. | [`decision-50-policy-no-number-shown.md`](../../docs/decision-50-policy-no-number-shown.md) |  |
| **٥١** | في سجلِّ الموافقات، كلُّ سطرٍ يقول صاحبُه «عميل محتمل» أو عميلاً فعليّاً — لأنّ نوعَ الموافقةِ يختلف بينهما، وهذا فرقٌ يسأل عنه قانونُ حمايةِ البيانات. | [`decision-51-kind-marker-returns-because.md`](../../docs/decision-51-kind-marker-returns-because.md) |  |
| **٥٢** | طلع إنذار أمني على مكتبة جاهزة نستعملها في رفع الملفات. قسنا وطلع إنه ما بيأثر على نظامنا. فسجلناه «ما بيأثر» — ومعه اختبار يحمي هذا الكلام. | [`decision-52-security-advisory-recorded-exposed.md`](../../docs/decision-52-security-advisory-recorded-exposed.md) |  |
| **٥٣** | في جدول الرقابة الداخلية، صنف السجل ورقمه صاروا في خانة واحدة. والنتيجة إن العمودين انطووا في عمود واحد اسمه يسمّي السجل. | [`decision-53-type-record-number-cell.md`](../../docs/decision-53-type-record-number-cell.md) |  |
| **٥٤** | لمّا فحص رقابي يقرأ أول عدد محدد من السجلات وبس، الشاشة تكتب بصراحة إن النتيجة غير مكتملة، وتقول كم سجلاً فُحِص. | [`decision-54-test-did-scan-everything.md`](../../docs/decision-54-test-did-scan-everything.md) |  |
| **٥٥** | عندنا علامة واحدة شغلها تجلس جنب تاريخ أو رقم وتقول إن الموعد فات. وعنوان العمود يقول التواريخ لشو — فالخانة ما تحتاج تشرح نفسها. | [`decision-55-overdue-marker-sits-beside.md`](../../docs/decision-55-overdue-marker-sits-beside.md) |  |
| **٥٦** | لما يُسجَّل حادث أمني أو حادث بيانات، وصف إجراءات الاحتواء الفورية إلزامي — ومعه وقته. | [`decision-56-containment-actions-required-timestamped.md`](../../docs/decision-56-containment-actions-required-timestamped.md) |  |
| **٥٧** | في دور في المكتب ما بيصير يملك ملف عميل أبداً. فشاشة العملاء عنده كانت بتفلتر على «العملاء اللي أملكهم» — فتطلع فاضية دائماً وتقول إنه ما في عملاء. والقرار: هو يشوف الكل. | [`decision-57-role-can-customer-sees.md`](../../docs/decision-57-role-can-customer-sees.md) |  |
| **٥٨** | موظف فتح شاشة تقرير وما اختار فترة — هو يسأل عن الشهر الحالي. أما حساب تقييم شهري، فعن الشهر اللي خلص. | [`decision-58-reader-s-month-scoring.md`](../../docs/decision-58-reader-s-month-scoring.md) |  |
| **٥٩** | اثنتا عشرة كلمة عربية على شاشات الموافقات والمطابقات ومراقبة العمليات — اعتمدتها المالكة. وإحدى عشرة منها كانت موجودة في النظام فعلاً، والجديدة واحدة، وهي بدّلت كلمة كانت موجودة وغلط. | [`decision-59-twelve-words-eleven-them.md`](../../docs/decision-59-twelve-words-eleven-them.md) |  |
| **٦٠** | على شاشات الحسابات والشكاوى والحوادث، سمّيتِ ثلاث حالات بكلماتك. وما في حالة رابعة — فلما ما تنطبق واحدة منهن، الشاشة تعرض شرطة، لا جملة من عند النظام. | [`decision-60-three-cases-dash-none.md`](../../docs/decision-60-three-cases-dash-none.md) |  |
| **٦٣** | عندنا كتالوج فيه أسماء شركات التأمين. ولما شركة تتسجّل فعلاً في النظام، بياناتها هي الأصح — وبيانات الكتالوج تنزاح. | [`decision-63-registered-company-outranks-catalogue.md`](../../docs/decision-63-registered-company-outranks-catalogue.md) |  |
| **٦٤** | التقييم المالي لشركة التأمين، وتاريخه، والجهة اللي أعطته — كلهم شي هذا المكتب سجّله وهو يقوم بواجب الحذر عند اختيار شركة. فهم ملك المكتب، والدليل المشترك ما يعرض أي واحد منهم أبداً. | [`decision-64-insurer-s-financial-rating.md`](../../docs/decision-64-insurer-s-financial-rating.md) |  |
| **٦٧** | حقول تسجيل المكتب وشركة التأمين تُقرأ بحذر: النظام ما يستنتج أن شركة مرخَّصة لنوعين من التأمين لأن بياناتها تسمح بذلك. | [`decision-67-licence-granted-reported.md`](../../docs/decision-67-licence-granted-reported.md) |  |
| **٧١** | عند تسجيل شركة التأمين، نأخذ تاريخ بداية الترخيص وتاريخ انتهائه. أما «هل الترخيص سارٍ؟» فما بنخزنها أبداً — بنحسبها من التاريخين. | [`decision-71-licence-standing-derived-stored.md`](../../docs/decision-71-licence-standing-derived-stored.md) |  |
| **٨٠** | أي شخص يقدر يسجّل تضارب مصالحه بنفسه، بلا ما يحتاج صلاحية. أما قراءة تضارب الآخرين، فعليها صلاحية يمنحها المكتب لمن يشاء. | [`decision-80-declaring-permission-reading-others.md`](../../docs/decision-80-declaring-permission-reading-others.md) |  |
| **٨٨** | مكتب يُسجَّل وما رفع وثيقة من وثائق المادة ١٠/أ — النظام يحفظ التسجيل ولا يرفضه. | [`decision-88-missing-article-10-document.md`](../../docs/decision-88-missing-article-10-document.md) |  |
| **٩٠** | في قاعدة في قاعدة البيانات تمنع تقييماً مالياً بلا تاريخه. وقرارك: الموظف ما يوصل لهذه القاعدة أبداً — الشاشة والخادم يمنعانه قبلها، برسالة تسمّي الحقلين. | [`decision-90-user-meet-database-constraint.md`](../../docs/decision-90-user-meet-database-constraint.md) |  |
| **٩٢** | لمّا يُفرَض جزاء على مكتب، مشغّل المنصة يشوف شياً واحداً: إن هذا المكتب ما يقدر يُصدِر. ولا يشوف مرجع القرار، ولا سنده، ولا تاريخ نفاذه، ولا تاريخ انتهائه، ولا الكتاب نفسه، ولا نوعه. | [`decision-92-provider-sees-fact-about.md`](../../docs/decision-92-provider-sees-fact-about.md) |  |
| **٩٣** | لمّا يُمسَح تقييم شركة التأمين، تاريخه يُمسَح معه في نفس العملية. وجواب الخادم ما يحمل أي أثر لقيود قاعدة البيانات. | [`decision-93-clearing-rating-clears-date.md`](../../docs/decision-93-clearing-rating-clears-date.md) |  |
| **٩٤** | أي اسم عربي لصلاحية، وأي جملة عربية جديدة، قرارك أنتِ. والنظام ما يكتب واحدة من عنده ولا يترجم. | [`decision-94-arabic-owner-s-system.md`](../../docs/decision-94-arabic-owner-s-system.md) |  |
| **٩٨** | كلُّ زرِّ تاريخٍ أو مهلةٍ صلاحيةٌ مستقلةٌ باسمها. **ووُسِّع منطقُه:** الرمزُ الواحدُ ما يحرس فعلَين مختلفَي الأثر — واحدٌ لا يُرجَع أو يغيّر مصيرَ السجلّ، وآخرُ مجرّدُ قراءةٍ أو مسوّدة. | [`decision-98-widened-and-concentration.md`](../../docs/decision-98-widened-and-concentration.md) |  |
| **١٢٢** | القناة اللي كنا بنفكر نطلب فيها من البنك المركزي قائمة تربط فروع الترخيص بأنواع التأمين عندنا — مقفولة. لا نطلب، ولا نبني. | [`decision-122-we-do-request-list.md`](../../docs/decision-122-we-do-request-list.md) | 🔴 **نعم** |

## الأربعةُ المعلَّمةُ «قُرِّر ولم يُبنَ» — وهذا مقصودٌ لا نقص

**القرارُ ٩** — عمودُ ربطِ فروعِ الترخيصِ بأنواعِ التأمينِ لا يُبنى قبل وصولِ القائمةِ الرسميّةِ التي تملّيه.
**القرارُ ٢٠** — وحدةُ عدِّ الفروعِ لحسابِ رأسِ المالِ قيدَ التحقّق؛ الرقمُ يُعرَض ومعه على الشاشتَين أنّه كذلك.
**القرارُ ٤٦** — ستُّ عائلاتِ سجلاتٍ بلا رقمٍ إنسانيٍّ؛ مؤجَّلةٌ إلى مديول ٧ لأنّ إعطاءَها رقماً يعني اختراعَ أوّلِ نظامِ ترقيمٍ في المنتج.
**القرارُ ١٢٢** — قناةُ الطلبِ من البنكِ المركزيِّ مقفولة.

⟶ **والثلاثةُ ٩ و٢٠ و١٢٢ مربوطون: لا نطلب، ولا نبني على فراغ، ولا نقول «محسوم» عن غيرِ المحسوم.**

**ومن يقرأ هذا العمودَ لازم يفهمه هيك:** **ليس «شغلٌ ناقص».** هو **«قرارٌ أُخِذَ بأن لا يُبنى، ومعه شرطُ إعادةِ الفتحِ مكتوبٌ سلفاً»**. ⟶ **فمن يبنيه بلا الشرطِ يخالف قراراً، لا يُكمل نقصاً.**

## ما لا يحتويه هذا الفهرس

**القراراتُ التي لم تُذكَر في الكودِ بعد.** الفهرسُ مبنيٌّ على ما يَستشهدُ به الكودُ فعلاً — **فهو يجاوب سؤالَ من يقرأ الكود، لا يجاوب «كلُّ ما قرّرَته المالكةُ منذ البداية».** وذاك سجلٌّ آخر، وهو عند المالكة.

