theory Full
  imports Main
begin

section "Working with Infinite Lists"

type_synonym 's behaviour = "nat ⇒ 's"

(* get the behaviour from the nth state onwards *)
definition i_drop :: "nat ⇒ 's behaviour ⇒ 's behaviour"
  where i_drop_def[simp]: "i_drop n σ ≡ λk. σ (n + k)"

(* get the first n states of the behaviour *)
definition i_take :: "nat ⇒ 's behaviour ⇒ 's list"
  where i_take_def[simp]: "i_take n σ ≡ [σ i. i ← [0..<n]]"

(* prefix a behaviour with a (finite) list of states *)
definition i_append :: "'s list ⇒ 's behaviour ⇒ 's behaviour" (infixr "⌢" 65)
  where i_append_def: "xs ⌢ σ ≡
    λn. if n < length xs
      then xs ! n
      else σ (n - length xs)"

type_synonym 's property = "'s behaviour ⇒ bool"

section "Syntax Sugar"

(* since we're overloading a bunch of logic operators *)
declare [[syntax_ambiguity_warning = false]]

abbreviation(input) models :: "'s behaviour ⇒ ('s behaviour ⇒ bool) ⇒ bool" (infix "⊨" 15)
  where "models σ p ≡ p σ"

abbreviation pNot :: "'s property ⇒ 's property" ("¬_" [40] 40)
  where "pNot p ≡ λσ. ¬(p σ)"

abbreviation pConj :: "'s property ⇒ 's property ⇒ 's property" (infix "∧" 35)
  where "pConj p q ≡ λσ. (p σ) ∧ (q σ)"

abbreviation pDisj :: "'s property ⇒ 's property ⇒ 's property" (infix "∨" 30)
  where "pDisj p q ≡ λσ. (p σ) ∨ (q σ)"

abbreviation pImp :: "'s property ⇒ 's property ⇒ 's property" (infixr "⟶" 25)
  where "pImp p q ≡ λσ. (p σ) ⟶ (q σ)"

abbreviation pTrue :: "'s property"
  where "pTrue ≡ λ_. True"

abbreviation pFalse :: "'s property"
  where "pFalse ≡ λ_. False"

section "Safety and Liveness"

definition safety :: "'s property ⇒ bool"
  where "safety P ≡ ∀σ. ¬(σ ⊨ P) ⟶
    (∃i. ∀β. ¬(i_take i σ ⌢ β ⊨ P))"

definition liveness :: "'s property ⇒ bool"
  where "liveness P ≡ ∀α. ∃β. α ⌢ β ⊨ P"

section "A Detour Into Topology"

definition limit_closure :: "'s property ⇒ 's property"
  where "limit_closure P ≡
    λσ. ∀n. ∃σ'. (σ' ⊨ P) ∧ (i_take n σ = i_take n σ')"

lemma limit_closure_subset[intro]: "σ ⊨ P ⟹ σ ⊨ limit_closure P"
  unfolding limit_closure_def i_drop_def
  by auto

lemma limit_closure_idem[simp]: "limit_closure (limit_closure P) = limit_closure P"
  unfolding limit_closure_def i_take_def
  by fastforce

definition limit_closed :: "'s property ⇒ bool"
  where "limit_closed P ≡ (limit_closure P) = P"

lemma limit_closed_forall[simp]:
    "limit_closed P = (∀σ. (σ ⊨ limit_closure P) ⟶ (σ ⊨ P))"
  unfolding limit_closed_def
  by auto

definition dense :: "'s property ⇒ bool"
  where "dense P ≡ (limit_closure P) = pTrue"

lemma dense_forall[simp]: "dense P = (∀σ. σ ⊨ limit_closure P)"
  using dense_def by auto

section "Four Big Lemmas"

(*
lemma safety_is_closed: "safety P ⟹ limit_closed P"
  sorry

lemma closed_is_safety: "limit_closed P ⟹ safety P"
  sorry

theorem safety_closed[simp]: "safety P = limit_closed P"
  using closed_is_safety safety_is_closed by blast

lemma liveness_is_dense: "liveness P ⟹ dense P"
  sorry

lemma dense_is_liveness: "dense P ⟹ liveness P"
  sorry

theorem liveness_dense[simp]: "liveness P = dense P"
  using dense_is_liveness liveness_is_dense by blast
*)

section "Liveness Is Dense"

lemma liveness_is_dense: "liveness P ⟹ dense P"
  unfolding liveness_def dense_forall limit_closure_def
  apply (intro allI)
  apply (erule_tac x="i_take n σ" in allE)
  apply (erule exE)
  apply (rule_tac x="(i_take n σ) ⌢ β" in exI)
  by (simp add: i_append_def)

section "Dense Is Liveness"

lemma append_inv[simp]: "i_take (length a) (a ⌢ b) = a"
  by (simp add: i_append_def map_upt_eqI)

lemma take_append_drop[simp]: "i_take n xs ⌢ i_drop n xs = xs"
  unfolding i_take_def i_drop_def i_append_def
  by force

lemma dense_is_liveness: "dense P ⟹ liveness P"
  unfolding liveness_def dense_forall limit_closure_def
  apply (rule allI)
  apply (erule_tac x="α ⌢ _" in allE)
  apply (erule_tac x="length α" in allE)
  apply (erule exE)
  apply (rule_tac x="i_drop (length α) σ'" in exI)
  by (metis append_inv take_append_drop)

theorem liveness_dense[simp]: "liveness P = dense P"
  using dense_is_liveness liveness_is_dense by blast

section "Safety Is Closed"

lemma safety_is_closed: "safety P ⟹ limit_closed P"
  unfolding safety_def limit_closed_forall limit_closure_def
  by (metis take_append_drop)

section "Closed Is Safety"

lemma not_limit_closure: "(σ ⊨ ¬(limit_closure P)) =
    (∃n. ∀σ'. (σ' ⊨ P) ⟶ (i_take n σ ≠ i_take n σ'))"
  unfolding limit_closure_def
  by blast

lemma closed_is_safety: "limit_closed P ⟹ safety P"
  unfolding safety_def limit_closed_forall
  apply (intro allI impI)
  apply (erule_tac x="σ" in allE)
  apply (case_tac "limit_closure P σ")
   subgoal by simp
  apply (thin_tac "σ ⊨ ¬P")
  apply (thin_tac "σ ⊨ limit_closure P ⟶ P")
  apply (subst (asm) not_limit_closure)
  apply (erule exE)
  apply (rule_tac x="n" in exI)
  by (metis append_inv i_take_def length_map take_append_drop)

theorem safety_closed[simp]: "safety P = limit_closed P"
  using closed_is_safety safety_is_closed by blast

section "Alpern and Schneider"

theorem alpern_schneider: "∃S L. safety S ∧ liveness L ∧ (P = (S ∧ L))"
  apply (rule_tac x="limit_closure P" in exI)
  apply (rule_tac x="¬((limit_closure P) ∧ ¬P)" in exI)
  apply (intro conjI)
    subgoal by simp
   subgoal by (metis (mono_tags, lifting) dense_def dense_is_liveness not_limit_closure)
  subgoal by auto
  done

end
