//! HSA-001 Virtue Passport — L7-hardened mint
//! Security review: 2026-08-14

use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, MintTo};

declare_id!("StoicMatrix1111111111111111111111111111111");

pub const DEFAULT_VIRTUE_THRESHOLD: u64 = 70;
pub const MAX_NAME_LEN: usize = 32;
pub const MAX_SYMBOL_LEN: usize = 10;
pub const MAX_URI_LEN: usize = 200;
pub const MAX_CONSTITUTION_ID_LEN: usize = 64;

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum PassportStage {
    Untrusted = 0,
    Provisional = 1,
    Trusted = 2,
}

#[program]
pub mod stoic_matrix {
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>,
        auth_bump: u8,
        virtue_threshold: u64,
    ) -> Result<()> {
        let state = &mut ctx.accounts.state;
        state.authority = ctx.accounts.authority.key();
        state.auth_bump = auth_bump;
        state.virtue_threshold = if virtue_threshold == 0 {
            DEFAULT_VIRTUE_THRESHOLD
        } else {
            virtue_threshold
        };
        state.mainnet_locked = false;
        Ok(())
    }

    pub fn mint_virtue_passport(
        ctx: Context<MintVirtuePassport>,
        name: String,
        symbol: String,
        uri: String,
        virtue_score: u64,
        passport_stage: PassportStage,
        constitution_id: String,
    ) -> Result<()> {
        let state = &ctx.accounts.state;

        require!(name.len() <= MAX_NAME_LEN, StoicError::StringTooLong);
        require!(symbol.len() <= MAX_SYMBOL_LEN, StoicError::StringTooLong);
        require!(uri.len() <= MAX_URI_LEN, StoicError::StringTooLong);
        require!(constitution_id.len() <= MAX_CONSTITUTION_ID_LEN, StoicError::StringTooLong);

        require_keys_eq!(
            ctx.accounts.authority.key(),
            state.authority,
            StoicError::UnauthorizedAuthority
        );

        require!(
            virtue_score >= state.virtue_threshold,
            StoicError::InsufficientVirtueScore
        );

        if state.mainnet_locked {
            require!(
                passport_stage != PassportStage::Untrusted,
                StoicError::UntrustedStageForbiddenOnMainnet
            );
        }

        let signer_seeds = &[b"program-authority".as_ref(), &[state.auth_bump]];
        let signer = &[&signer_seeds[..]];

        token::mint_to(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                MintTo {
                    mint: ctx.accounts.nft_mint.to_account_info(),
                    to: ctx.accounts.nft_token_account.to_account_info(),
                    authority: ctx.accounts.program_pda_authority.to_account_info(),
                },
                signer,
            ),
            1,
        )?;

        emit!(VirtuePassportMinted {
            nft_mint: ctx.accounts.nft_mint.key(),
            recipient: ctx.accounts.nft_token_account.owner,
            virtue_score,
            passport_stage: passport_stage as u8,
            constitution_id,
            threshold_used: state.virtue_threshold,
            timestamp: Clock::get()?.unix_timestamp,
        });

        Ok(())
    }

    pub fn update_passport_metadata(
        ctx: Context<UpdatePassportMetadata>,
        new_uri: String,
        new_virtue_score: u64,
    ) -> Result<()> {
        require!(new_uri.len() <= MAX_URI_LEN, StoicError::StringTooLong);

        require_keys_eq!(
            ctx.accounts.authority.key(),
            ctx.accounts.state.authority,
            StoicError::UnauthorizedAuthority
        );

        emit!(MetadataUpdated {
            nft_mint: ctx.accounts.nft_mint.key(),
            new_uri,
            virtue_score: new_virtue_score,
            timestamp: Clock::get()?.unix_timestamp,
        });

        Ok(())
    }

    pub fn set_mainnet_locked(ctx: Context<SetMainnetLocked>, locked: bool) -> Result<()> {
        require_keys_eq!(
            ctx.accounts.authority.key(),
            ctx.accounts.state.authority,
            StoicError::UnauthorizedAuthority
        );
        ctx.accounts.state.mainnet_locked = locked;
        Ok(())
    }

    pub fn set_virtue_threshold(
        ctx: Context<SetVirtueThreshold>,
        new_threshold: u64,
    ) -> Result<()> {
        require_keys_eq!(
            ctx.accounts.authority.key(),
            ctx.accounts.state.authority,
            StoicError::UnauthorizedAuthority
        );
        require!(
            new_threshold > 0 && new_threshold <= 100,
            StoicError::InvalidThreshold
        );
        ctx.accounts.state.virtue_threshold = new_threshold;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 1 + 8 + 1,
        seeds = [b"state"],
        bump
    )]
    pub state: Account<'info, StoicState>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintVirtuePassport<'info> {
    #[account(seeds = [b"state"], bump)]
    pub state: Account<'info, StoicState>,
    pub authority: Signer<'info>,
    /// CHECK: PDA – mint & update authority
    #[account(seeds = [b"program-authority"], bump = state.auth_bump)]
    pub program_pda_authority: AccountInfo<'info>,
    #[account(mut)]
    pub nft_mint: Account<'info, Mint>,
    #[account(mut)]
    pub nft_token_account: Account<'info, TokenAccount>,
    /// CHECK: metadata account
    #[account(mut)]
    pub metadata_account: AccountInfo<'info>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct UpdatePassportMetadata<'info> {
    #[account(seeds = [b"state"], bump)]
    pub state: Account<'info, StoicState>,
    pub authority: Signer<'info>,
    /// CHECK: PDA
    #[account(seeds = [b"program-authority"], bump = state.auth_bump)]
    pub program_pda_authority: AccountInfo<'info>,
    /// CHECK: mint
    pub nft_mint: AccountInfo<'info>,
    #[account(mut)]
    pub metadata_account: AccountInfo<'info>,
}

#[derive(Accounts)]
pub struct SetMainnetLocked<'info> {
    #[account(mut, seeds = [b"state"], bump)]
    pub state: Account<'info, StoicState>,
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct SetVirtueThreshold<'info> {
    #[account(mut, seeds = [b"state"], bump)]
    pub state: Account<'info, StoicState>,
    pub authority: Signer<'info>,
}

#[account]
pub struct StoicState {
    pub authority: Pubkey,
    pub auth_bump: u8,
    pub virtue_threshold: u64,
    pub mainnet_locked: bool,
}

#[event]
pub struct VirtuePassportMinted {
    pub nft_mint: Pubkey,
    pub recipient: Pubkey,
    pub virtue_score: u64,
    pub passport_stage: u8,
    pub constitution_id: String,
    pub threshold_used: u64,
    pub timestamp: i64,
}

#[event]
pub struct MetadataUpdated {
    pub nft_mint: Pubkey,
    pub new_uri: String,
    pub virtue_score: u64,
    pub timestamp: i64,
}

#[error_code]
pub enum StoicError {
    #[msg("Unauthorized")]
    UnauthorizedAuthority,
    #[msg("Insufficient Virtue Score")]
    InsufficientVirtueScore,
    #[msg("Untrusted stage forbidden on mainnet")]
    UntrustedStageForbiddenOnMainnet,
    #[msg("Virtue threshold must be 1..=100")]
    InvalidThreshold,
    #[msg("String exceeds maximum allowed length")]
    StringTooLong,
}
